"""The checks. Every check only reads; nothing here changes the home.

Each check returns a list of Finding objects. A finding is one "thing to look at", with the items behind it.
Each item has a key, so a person can mark it "Keep" and it never shows again.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ATTR_FRIENDLY_NAME, ATTR_RESTORED, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers import label_registry as lr
from homeassistant.loader import async_get_loaded_integration
from homeassistant.util import dt as dt_util

from .const import (
    BACKUP_FRESH,
    BACKUP_OLD,
    CHATTY_EVERY,
    CHATTY_MIN_HOURS,
    CHATTY_SHOWN,
    WEAK_AFTER,
    WEAK_LQI,
    WEAK_RSSI,
    BATTERY_LOW,
    DATABASE_BIG,
    IDLE_AFTER,
    IDLE_NEW,
    STORAGE_FULL,
    STORAGE_SOON_DAYS,
    LOG_WINDOW,
    NEW_ERROR_AFTER,
    NOTE_HOURS,
    CORPUS_MAX_BYTES,
    CORPUS_SKIP_DIRS,
    CORPUS_SKIP_NAME_PARTS,
    CORPUS_STORAGE_PREFIXES,
    DOMAIN,
    HELPER_DOMAINS,
    HELPER_MIN_AGE,
    BACK_AFTER,
    BACK_AFTER_UNNAMED,
    KEEPS_DROPPING,
    UNAVAILABLE_AFTER,
    TEMPLATE_HELPER_DOMAINS,
    UNAVAILABLE_SINCE_START_AFTER,
)
from .logwatch import LogWatch, is_wrapper, redact
from .meanings import meaning_of

_LOGGER = logging.getLogger(__name__)

RELOADABLE_STATES = {ConfigEntryState.SETUP_ERROR, ConfigEntryState.SETUP_RETRY}
IGNORE_LABEL = "checkup_ignore"
FAILED_STATES = {
    ConfigEntryState.SETUP_ERROR,
    ConfigEntryState.SETUP_RETRY,
    ConfigEntryState.MIGRATION_ERROR,
    ConfigEntryState.FAILED_UNLOAD,
}
_START_SLACK = timedelta(minutes=10)
_FAILED_ONCE: set[int] = set()
_HELPER_ID = re.compile(r"(?<![\w.])((?:" + "|".join(HELPER_DOMAINS) + r")\.[a-z0-9_]+)(?![\w])")


@dataclass
class Item:
    key: str  # stable id used by "Keep"
    name: str  # friendly words, never a raw id when a name exists
    id: str  # the entity id, device id or automation id, for people who want it
    info: str = ""
    link: str = ""
    hint: str = ""  # for log items: the code of what it means ("timeout", "signin", ...), shown in words by the page
    new: bool = False  # first seen in the last 24 hours
    startup: bool = False  # for log items: only right after a restart
    times: int = 0  # for log items: how often in the last 24 hours, so the page can show it at a glance
    last: str = ""  # for log items: the clock time it was last seen
    last_at: float = 0  # for log items: the same moment as a timestamp, so the page can add the day when it was not today
    # For broken automation steps: the one-tap fix Home Checkup can offer, and when the automation last ran.
    fix: str = ""  # "use_new" (a renamed entity), "remove_step" (only that step is broken), "turn_off", or "disable" (an offline device)
    old: str = ""  # the missing entity id
    to: str = ""  # use_new: the entity that looks like its new name
    to_name: str = ""
    choose: bool = False  # no new name was found: the person can choose another entity of the same kind
    # The automation or script is written by hand in a YAML file, where no button can change it: where to look.
    file: str = ""  # "packages/scripts.yaml"
    line: int = 0
    gone: str = ""  # turn_off: the integration that was removed ("Roomba")
    gone_at: str = ""  # turn_off: when, ISO date
    last_ran: str = ""  # ISO time, "" when it never ran
    # For things that are offline: since when (ISO), whether it may be longer, and for a device how many entities.
    since: str = ""
    or_earlier: bool = False
    parts: int = 0
    of: int = 0  # a device that is partly offline: how many entities it has in all
    # For a log error about something that could not be reached and that works again: when the errors began.
    back: bool = False
    back_from: float = 0
    risk: str = ""  # a waiting update: "breaking" (its notes say so) or "major" (a big version step)
    # hint "moved": the device Home Assistant now sees at another address than the one the integration uses.
    device: str = ""
    seen_at: str = ""
    # For things that are offline: the automations and scripts that use them (names), and how many in all.
    used_by: list[str] = field(default_factory=list)
    used_n: int = 0
    # For storage: how much (GB), of how much, and in about how many days it is full at this rate.
    amount: float = 0
    total: float = 0
    days: int = 0
    good: bool = False  # "Before you update": this point is fine
    every: int = 0  # a chatty entity: it writes to the history about every N seconds


@dataclass
class Finding:
    kind: str
    title: str
    detail: str
    severity: str = "warning"  # "warning" counts as a thing to look at; "info" is shown but not counted
    integration: str | None = None
    integration_name: str | None = None
    link: str = ""
    items: list[Item] = field(default_factory=list)
    # False: shown on the page under "To watch". Not counted anywhere and not in the Repairs note,
    # so the page, the sensor and the note always show the same number.
    in_note: bool = True
    # The next step the page offers (log findings): a code the page shows in words, and where it goes.
    action: str = ""  # "update", "signin", "devices", "template", "logs"
    action_link: str = ""
    action_info: str = ""  # for "update": the new version
    back: bool = False  # log errors about something that works again: shown as good news, not counted

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["count"] = len(self.items)
        return data


def integration_name(hass: HomeAssistant, domain: str | None) -> str:
    if not domain:
        return "Home Assistant"
    try:
        return async_get_loaded_integration(hass, domain).name
    except Exception:  # noqa: BLE001 - not loaded, or not an integration
        return domain.replace("_", " ").title()


def update_for(hass: HomeAssistant, domain: str | None) -> str | None:
    """The new version, when an update that may fix this integration is ready. None when there is none.

    Built-in integrations come with Home Assistant itself, so for them it is Home Assistant's own update.
    Custom integrations: an update entity from HACS whose title names the integration.
    """
    built_in = True
    name = ""
    if domain:
        try:
            integration = async_get_loaded_integration(hass, domain)
            built_in = integration.is_built_in
            name = integration.name.lower()
        except Exception:  # noqa: BLE001
            built_in = False
            name = domain.replace("_", " ")
    ent_reg = er.async_get(hass)
    for state in hass.states.async_all("update"):
        if state.state != "on":
            continue
        entry = ent_reg.async_get(state.entity_id)
        platform = entry.platform if entry else ""
        title = str(state.attributes.get("title") or state.attributes.get(ATTR_FRIENDLY_NAME) or "").lower()
        latest = str(state.attributes.get("latest_version") or "")
        if built_in and (platform == "hassio" and "core" in state.entity_id or state.entity_id.endswith("home_assistant_core_update")):
            return latest
        if not built_in and platform == "hacs" and (name and name in title or (domain or "~") in state.entity_id):
            return latest
    return None


_ACTION_FOR_HINT = {
    "signin": "signin",
    "offline": "devices",
    "unreachable": "devices",
    "timeout": "devices",
    "template": "template",
    "missing": "template",
}


def next_step(hass: HomeAssistant, domain: str | None, hints: list[str]) -> tuple[str, str, str]:
    """The one next step for a group of log errors: an update first (it fixes most), then by cause."""
    integration_page = f"/config/integrations/integration/{domain}" if domain else "/config/logs"
    version = update_for(hass, domain)
    if version is not None:
        return "update", "/config/updates", version
    for hint in hints:
        action = _ACTION_FOR_HINT.get(hint)
        if action == "template":
            return action, "/config/lovelace/dashboards" if not domain else integration_page, ""
        if action:
            return action, integration_page, ""
    return "logs", "/config/logs", ""


def _plural(n: int, one: str, many: str | None = None) -> str:
    return f"{n} {one if n == 1 else (many or one + 's')}"


def _entity_name(hass: HomeAssistant, entry: er.RegistryEntry | None, entity_id: str) -> str:
    state = hass.states.get(entity_id)
    if state and state.attributes.get(ATTR_FRIENDLY_NAME):
        return str(state.attributes[ATTR_FRIENDLY_NAME])
    if entry and (entry.name or entry.original_name):
        return str(entry.name or entry.original_name)
    return entity_id.split(".", 1)[-1].replace("_", " ").capitalize()


# ---- A device that moved to a new address -----------------------------------------------------------------

_IP_IN_TEXT = re.compile(r"(?<![\d.])((?:\d{1,3}\.){3}\d{1,3})(?![\d.])")
_LOCAL_IP = re.compile(r"^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|169\.254\.)")


@callback
def seen_addresses(hass: HomeAssistant) -> dict[str, str]:
    """Hardware address (MAC) -> the IP address where Home Assistant sees that device on the network now.

    Home Assistant already knows this: from router integrations (their device trackers) and from what it hears
    on the network. Nothing is scanned here, and no settings of any integration are read.
    """
    seen: dict[str, str] = {}
    try:
        from homeassistant.components.dhcp.helpers import async_get_address_data_internal  # noqa: PLC0415

        for mac, data in async_get_address_data_internal(hass).items():
            if data.get("ip"):
                seen[dr.format_mac(mac)] = str(data["ip"])
    except Exception:  # noqa: BLE001 - not set up, or it changed: the router integrations below still count
        pass
    for state in hass.states.async_all("device_tracker"):
        mac, ip = state.attributes.get("mac"), state.attributes.get("ip")
        if mac and ip and state.state == "home":
            seen[dr.format_mac(str(mac))] = str(ip)
    return seen


@callback
def _down(hass: HomeAssistant, ent_reg: er.EntityRegistry, device_id: str) -> bool:
    states = [
        hass.states.get(e.entity_id)
        for e in er.async_entries_for_device(ent_reg, device_id)
        if e.disabled_by is None
    ]
    return all(s is None or s.state == STATE_UNAVAILABLE for s in states)


@callback
def _any_device_down(hass: HomeAssistant, entry_ids: list[str]) -> bool:
    dev_reg = dr.async_get(hass)
    ent_reg = er.async_get(hass)
    return any(
        er.async_entries_for_device(ent_reg, device.id) and _down(hass, ent_reg, device.id)
        for entry_id in entry_ids
        for device in dr.async_entries_for_config_entry(dev_reg, entry_id)
    )


@callback
def _answers_elsewhere(hass: HomeAssistant, entry_ids: list[str]) -> bool:
    """True when another integration talks to the same hardware (same MAC) right now.

    Then the device is on and its address is right. Only this one connection is closed, for example a service
    that was turned off in the app of the device.
    """
    dev_reg = dr.async_get(hass)
    ent_reg = er.async_get(hass)
    macs = {
        dr.format_mac(mac)
        for entry_id in entry_ids
        for device in dr.async_entries_for_config_entry(dev_reg, entry_id)
        for kind, mac in device.connections
        if kind == dr.CONNECTION_NETWORK_MAC
    }
    if not macs:
        return False
    for device in dev_reg.devices.values():
        if not any(k == dr.CONNECTION_NETWORK_MAC and dr.format_mac(m) in macs for k, m in device.connections):
            continue
        for entity in er.async_entries_for_device(ent_reg, device.id):
            if entity.config_entry_id in entry_ids or entity.disabled_by is not None:
                continue
            state = hass.states.get(entity.entity_id)
            if state is not None and state.state != STATE_UNAVAILABLE and not state.attributes.get(ATTR_RESTORED):
                return True
    return False


@callback
def address_hint(
    hass: HomeAssistant, entry_ids: list[str], text: str, seen: dict[str, str], need_down: bool = False
) -> tuple[str, str, str]:
    """For something local that cannot be reached: ("moved", device name, new IP), ("address", "", "") or ("", "", "").

    "moved" needs proof: the error names an address, and the same hardware (by its MAC) is now seen at another one.
    When Home Assistant sees the device at the very address the error names, the address is right: no hint.
    """
    named = set(_IP_IN_TEXT.findall(text or ""))
    dev_reg = dr.async_get(hass)
    ent_reg = er.async_get(hass)
    here: list[tuple[str, str]] = []  # devices of these entries that the network shows, with their address now
    local = any(_LOCAL_IP.match(ip) for ip in named)
    for entry_id in entry_ids:
        for device in dr.async_entries_for_config_entry(dev_reg, entry_id):
            for kind, mac in device.connections:
                if kind != dr.CONNECTION_NETWORK_MAC:
                    continue
                local = True
                ip = seen.get(dr.format_mac(mac))
                if ip and not (need_down and not _down(hass, ent_reg, device.id)):
                    here.append((device.name_by_user or device.name or "", ip))
    if not local:
        return "", "", ""
    if not need_down and _answers_elsewhere(hass, entry_ids):
        return "closed", "", ""
    if any(ip in named for _, ip in here):
        return "", "", ""
    if named and len(here) == 1 and here[0][0]:
        return "moved", here[0][0], here[0][1]
    return "address", "", ""


# ---- 1. Log: warnings and errors grouped by integration and cause ---------------------------------------


@callback
def _clock(when: float) -> str:
    return dt_util.as_local(dt_util.utc_from_timestamp(when)).strftime("%H:%M")


REACH_HINTS = frozenset({"timeout", "unreachable", "dropped", "offline", "dns"})
_ENTITY_IN_TEXT = re.compile(r"\b([a-z][a-z0-9_]*\.[a-z0-9_]+)\b")


@callback
def _works_again(hass: HomeAssistant, group: Any, now: float, drops: dict[str, list[float]], key: str) -> str:
    """"back": a could-not-reach error whose device works again. "flaky": it did that 3 times this week. Else "".

    With the entity named in the error we can look: it must be available now, and quiet for BACK_AFTER.
    Without a name only time can tell, so the quiet time is longer.
    """
    text = f"{group.template} {group.sample} {group.cause}"
    if meaning_of(text) not in REACH_HINTS:
        return ""
    named = [e for e in dict.fromkeys(_ENTITY_IN_TEXT.findall(f"{group.sample} {group.cause}")) if hass.states.get(e)]
    if any(hass.states.get(e).state == STATE_UNAVAILABLE for e in named):
        return ""
    quiet = BACK_AFTER if named else BACK_AFTER_UNNAMED
    if now - group.last_seen < quiet.total_seconds():
        return ""
    week = now - 7 * 86400
    times = [t for t in drops.get(key, []) if t >= week]
    if not times or group.last_seen - times[-1] > BACK_AFTER.total_seconds():
        times.append(group.last_seen)
    drops[key] = times
    return "flaky" if len(times) >= KEEPS_DROPPING else "back"


def check_log(
    hass: HomeAssistant,
    watch: LogWatch,
    now: float | None = None,
    keep: frozenset[str] = frozenset(),
    watching_since: float = 0.0,
    run_start: float = 0.0,
    drops: dict[str, list[float]] | None = None,
) -> list[Finding]:
    """One finding per integration and level. What goes in the Repairs note:

    1. Errors that keep coming back: seen outside start-up in at least NOTE_HOURS different hours of the last 24.
    2. Brand new errors, once Home Checkup has watched long enough to know they are new (after an update, say).
    Start-up noise (errors only in the first minutes after a restart) is shown, but not counted and not in the note.
    """
    now = now if now is not None else time.time()
    since = now - LOG_WINDOW.total_seconds()
    knows_normal = watching_since and now - watching_since >= NEW_ERROR_AFTER.total_seconds()
    # A start-up error is about one start. Errors from an earlier start leave the page as soon as Home Assistant
    # starts again (`run_start`: when this run began). If the error comes back at this start, it is shown again,
    # with the new time. So an old line never returns for a few minutes after a restart.
    drops = drops if drops is not None else {}
    seen = seen_addresses(hass)
    for key in [k for k, times in drops.items() if not times or times[-1] < now - 7 * 86400]:
        del drops[key]
    by_domain: dict[str | None, list] = defaultdict(list)
    for group, count in watch.groups(now):
        if run_start and group.last_seen < run_start and group.startup_only(since):
            continue
        if count and f"log:{group.domain}:{group.template}" not in keep:
            by_domain[group.domain].append((group, count))
    findings: list[Finding] = []
    for domain, groups in by_domain.items():
        errors = [(g, n) for g, n in groups if g.level in ("ERROR", "CRITICAL")]
        warnings = [(g, n) for g, n in groups if g.level not in ("ERROR", "CRITICAL")]
        # Could-not-reach errors whose device works again are good news: their own group, shown but not counted.
        state = {
            g.template: "" if g.startup_only(since) else _works_again(hass, g, now, drops, f"log:{domain}:{g.template}")
            for g, _ in errors
        }
        back_errors = [(g, n) for g, n in errors if state[g.template] == "back"]
        # Still failing, and about something local: maybe it moved to a new address.
        entry_ids = [e.entry_id for e in hass.config_entries.async_entries(domain)] if domain else []
        # A log error does not say which device it is about, so the words about the address are only used
        # while a whole device of this integration is offline. A camera that is slow now and then keeps its own words.
        moved = {}
        if entry_ids and _any_device_down(hass, entry_ids):
            moved = {
                g.template: hint
                for g, _ in errors
                if state[g.template] == "" and not g.startup_only(since)
                and meaning_of(f"{g.template} {g.sample} {g.cause}") in REACH_HINTS
                and (hint := address_hint(hass, entry_ids, f"{g.sample} {g.cause}", seen, need_down=True))[0]
            }
        errors = [(g, n) for g, n in errors if state[g.template] != "back"]
        name = integration_name(hass, domain)
        for level_groups, is_error, word, back in (
            (errors, True, "error", False),
            (back_errors, True, "error", True),
            (warnings, False, "warning", False),
        ):
            if not level_groups:
                continue
            total = sum(n for _, n in level_groups)
            causes = len(level_groups)
            startup = all(g.startup_only(since) for g, _ in level_groups)
            hours = {h for g, _ in level_groups for h, n in g.late.items() if n and h >= int(since // 3600)}
            new = bool(knows_normal) and any(
                g.first_seen >= since and g.first_seen >= watching_since + NEW_ERROR_AFTER.total_seconds() and not g.startup_only(since)
                for g, _ in level_groups
            )
            severity = "warning" if is_error and not startup and not back else "info"
            if back:
                detail = "It could not be reached for a while. It works again."
            elif startup:
                detail = "Only right after a restart. Usually harmless, but it hides real errors."
            elif causes == 1:
                detail = "One cause, repeated."
            else:
                detail = f"{causes} different causes."
            hints = [meaning_of(f"{g.template} {g.sample} {g.cause}") for g, _ in level_groups]
            action, action_link, action_info = next_step(hass, domain, hints) if is_error and not back else ("", "", "")
            findings.append(
                Finding(
                    kind="log_errors" if is_error else "log_warnings",
                    action=action,
                    action_link=action_link,
                    action_info=action_info,
                    title=f"{name} reported {_plural(total, word)} in the last 24 hours",
                    detail=detail,
                    severity=severity,
                    integration=domain,
                    integration_name=name,
                    back=back,
                    in_note=severity == "warning" and (len(hours) >= NOTE_HOURS or new),
                    link=f"/config/integrations/integration/{domain}" if domain else "/config/logs",
                    items=[
                        Item(
                            key=f"log:{domain}:{g.template}",
                            # A wrapper line ("Error doing job…") says nothing: the real error is the title.
                            name=g.cause if g.cause and is_wrapper(g.sample) else g.sample,
                            id=g.logger,
                            info=(
                                f"{_plural(n, 'time')}, only right after a restart, last at {_clock(g.last_seen)}"
                                if g.startup_only(since)
                                else f"{_plural(n, 'time')}, last at {_clock(g.last_seen)}"
                            ),
                            hint=(
                                "flaky"
                                if is_error and state.get(g.template) == "flaky"
                                else (is_error and not back and g.template in moved and moved[g.template][0])
                                or meaning_of(f"{g.template} {g.sample} {g.cause}")
                            ),
                            device=moved[g.template][1] if is_error and not back and g.template in moved else "",
                            seen_at=moved[g.template][2] if is_error and not back and g.template in moved else "",
                            back=back,
                            back_from=g.first_seen if back and g.first_seen >= since else 0,
                            startup=g.startup_only(since),
                            times=n,
                            last=_clock(g.last_seen),
                            last_at=g.last_seen,
                        )
                        for g, n in level_groups
                    ],
                )
            )
    return findings


# ---- 2. Integrations that did not start ------------------------------------------------------------------


@callback
def check_failed_integrations(hass: HomeAssistant, keep: frozenset[str] = frozenset()) -> list[Finding]:
    seen = seen_addresses(hass)
    items = []
    for entry in hass.config_entries.async_entries():
        if entry.state not in FAILED_STATES or entry.disabled_by is not None or entry.domain == DOMAIN:
            continue
        # It keeps trying and cannot reach something local: maybe that device moved to a new address.
        hint, device, seen_at = (
            address_hint(hass, [entry.entry_id], entry.reason or "", seen)
            if entry.state is ConfigEntryState.SETUP_RETRY and meaning_of(entry.reason or "") in REACH_HINTS
            else ("", "", "")
        )
        items.append(
            Item(
                key=f"entry:{entry.entry_id}",
                name=f"{integration_name(hass, entry.domain)}: {entry.title}",
                id=entry.entry_id,
                info=redact(entry.reason or "") or entry.state.value.replace("_", " "),
                link=f"/config/integrations/integration/{entry.domain}",
                hint=hint,
                device=device,
                seen_at=seen_at,
                # Home Assistant's own "Reload", one tap away. Only where a reload is allowed.
                fix="reload" if entry.state in RELOADABLE_STATES else "",
            )
        )
    items = [i for i in items if i.key not in keep]
    if not items:
        return []
    return [
        Finding(
            kind="failed_integrations",
            title=f"{_plural(len(items), 'integration')} did not start",
            detail="Their devices do not work until they start again. A restart or a new sign-in often helps.",
            link="/config/integrations",
            items=items,
        )
    ]


# ---- 3. Leftover entities and devices ----------------------------------------------------------------------


@callback
def check_leftovers(
    hass: HomeAssistant, keep: frozenset[str] = frozenset(), started_at: datetime | None = None
) -> list[Finding]:
    """Leftovers: entities and devices whose integration is gone, or that their integration no longer makes.

    "No longer makes" is only judged once Home Assistant has run for a day. Some integrations (iBeacon,
    Bluetooth devices) make their entities only when they hear the device, which can take a while after a start.
    """
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    loaded = set(hass.config.components)
    settled = started_at is not None and dt_util.utcnow() - started_at >= UNAVAILABLE_SINCE_START_AFTER
    entities: list[Item] = []
    for entry in ent_reg.entities.values():
        if entry.disabled_by is not None:
            continue
        reason = ""
        if entry.config_entry_id:
            config_entry = hass.config_entries.async_get_entry(entry.config_entry_id)
            if config_entry is None:
                reason = "Its integration was removed."
            elif config_entry.state is not ConfigEntryState.LOADED:
                continue  # a failed integration, reported on its own
        if not reason:
            state = hass.states.get(entry.entity_id)
            if settled and state is not None and state.attributes.get(ATTR_RESTORED) and entry.platform in loaded:
                reason = f"{integration_name(hass, entry.platform)} has not provided it since Home Assistant last started."
        if reason:
            entities.append(
                Item(
                    key=f"entity:{entry.entity_id}",
                    name=_entity_name(hass, entry, entry.entity_id),
                    id=entry.entity_id,
                    info=reason,
                    link="/config/entities",
                )
            )
    devices: list[Item] = []
    for device in _all_devices(dev_reg):
        if device.disabled_by is not None:
            continue
        entry_ids = _device_entry_ids(device)
        if entry_ids and all(hass.config_entries.async_get_entry(e) is None for e in entry_ids):
            devices.append(
                Item(
                    key=f"device:{device.id}",
                    name=device.name_by_user or device.name or "Unnamed device",
                    id=device.id,
                    info="Its integration was removed.",
                    link=f"/config/devices/device/{device.id}",
                )
            )
    entities = [i for i in entities if i.key not in keep]
    devices = [i for i in devices if i.key not in keep]
    findings = []
    if entities:
        findings.append(
            Finding(
                kind="leftover_entities",
                title=f"{_plural(len(entities), 'leftover entity', 'leftover entities')}",
                detail="Nothing provides them any more. They do nothing, but they fill lists and searches.",
                link="/config/entities",
                items=entities,
            )
        )
    if devices:
        findings.append(
            Finding(
                kind="leftover_devices",
                title=f"{_plural(len(devices), 'leftover device')}",
                detail="Their integration is gone. They do nothing now.",
                link="/config/devices/dashboard",
                items=devices,
            )
        )
    return findings


# ---- 4. Entities unavailable for a long time ----------------------------------------------------------------


# A wall tablet's own entities (Browser Mod, Fully Kiosk) go unavailable when the tablet sleeps. That is not a fault.
# The sensors of a phone or a computer (the companion app) do the same when the device sleeps or the app is closed.
SLEEPING_PLATFORMS = frozenset({"browser_mod", "fully_kiosk", "mobile_app"})
USED_BY_SHOWN = 4


@callback
def used_by(hass: HomeAssistant, entity_ids: list[str], device_id: str | None) -> list[str]:
    """The names of the automations and scripts that use these entities or this device. Switched-off ones are left out."""
    owners: dict[str, None] = {}
    try:
        from homeassistant.components import automation, script  # noqa: PLC0415

        for entity_id in entity_ids:
            for owner in (*automation.automations_with_entity(hass, entity_id), *script.scripts_with_entity(hass, entity_id)):
                owners[owner] = None
        if device_id:
            for owner in (*automation.automations_with_device(hass, device_id), *script.scripts_with_device(hass, device_id)):
                owners[owner] = None
    except Exception:  # noqa: BLE001 - automations or scripts are not set up: then nothing uses it
        return []
    names = []
    for owner in owners:
        state = hass.states.get(owner)
        if state is None or (owner.startswith("automation.") and state.state == "off"):
            continue
        names.append(str(state.attributes.get(ATTR_FRIENDLY_NAME) or owner))
    return sorted(names, key=str.lower)


@callback
def check_unavailable(
    hass: HomeAssistant,
    started_at: datetime | None,
    keep: frozenset[str] = frozenset(),
    memory: dict[str, list[Any]] | None = None,
) -> list[Finding]:
    """Things that have been offline for a long time. A device with nothing left that works is one line.

    Home Assistant forgets "unavailable since" at every restart. `memory` is our own note per entity:
    [the earliest moment we know it was offline, whether that moment is exact]. With it the date stays true
    across restarts, and a thing we already listed is listed again right after a restart.
    """
    now = dt_util.utcnow()
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    memory = memory if memory is not None else {}
    up_long = started_at is not None and now - started_at >= UNAVAILABLE_SINCE_START_AFTER

    # Forget what came back, was removed or was switched off.
    for entity_id in list(memory):
        state = hass.states.get(entity_id)
        entry = ent_reg.async_get(entity_id)
        if (state is not None and state.state != STATE_UNAVAILABLE) or (state is None and (entry is None or entry.disabled_by)):
            del memory[entity_id]

    lone: list[tuple[str, Any, datetime, bool]] = []  # entity id, registry entry, since, exact
    by_device: dict[str, list[tuple[str, Any, datetime, bool]]] = {}
    for state in hass.states.async_all():
        if state.state != STATE_UNAVAILABLE:
            continue
        noted = memory.get(state.entity_id)
        # Restored ones are leftovers or failed integrations, reported elsewhere. But while Home Assistant is
        # still starting, everything looks restored for a moment: what we already listed stays on the list.
        if state.attributes.get(ATTR_RESTORED) and not (noted and not up_long):
            continue
        entry = ent_reg.async_get(state.entity_id)
        if entry is not None and entry.platform in SLEEPING_PLATFORMS:
            continue
        since = state.last_changed
        # Before Home Assistant has finished starting there is no start time yet: all of it is "since the start".
        if started_at is None:
            at_start = now - since < UNAVAILABLE_SINCE_START_AFTER
        else:
            at_start = since <= started_at + _START_SLACK
        exact = not at_start  # "since the start" only says: at least that long
        if noted and at_start and noted[0] < since.timestamp():
            since, exact = dt_util.utc_from_timestamp(noted[0]), bool(noted[1])
        if not (now - since >= UNAVAILABLE_AFTER or (up_long and at_start) or (noted and at_start)):
            continue
        memory[state.entity_id] = [since.timestamp(), exact]
        row = (state.entity_id, entry, since, exact)
        if entry is not None and entry.device_id:
            by_device.setdefault(entry.device_id, []).append(row)
        else:
            lone.append(row)

    def words(since: datetime, exact: bool) -> str:
        day = dt_util.as_local(since).strftime("%-d %b")
        return f"Offline since {day}" if exact else f"Offline since {day} or earlier"

    items: list[Item] = []
    for device_id, rows in by_device.items():
        device = dev_reg.async_get(device_id)
        # One line for the device only when nothing of it works any more: every entity that is switched on is on the list.
        enabled = [e for e in er.async_entries_for_device(ent_reg, device_id) if e.disabled_by is None]
        if device is not None and 1 < len(rows) < len(enabled):
            # Part of the device is offline: still one line, so a device with many sensors does not fill the page.
            rows = [r for r in rows if f"unavailable:{r[0]}" not in keep]
            key = f"offline_parts:{device_id}"
            if key in keep or not rows:
                continue
            _, _, since, exact = min(rows, key=lambda r: r[2])
            items.append(
                Item(
                    key=key,
                    name=device.name_by_user or device.name or "Unnamed device",
                    id=device_id,
                    info=f"{words(since, exact)} · {len(rows)} of {len(enabled)} entities",
                    link=f"/config/devices/device/{device_id}",
                    since=since.isoformat(),
                    or_earlier=not exact,
                    parts=len(rows),
                    of=len(enabled),
                )
            )
            continue
        if device is None or len(rows) < len(enabled):
            lone.extend(rows)
            continue
        key = f"offline_device:{device_id}"
        if key in keep or all(f"unavailable:{entity_id}" in keep for entity_id, *_ in rows):
            continue
        _, _, since, exact = min(rows, key=lambda r: r[2])
        items.append(
            Item(
                key=key,
                name=device.name_by_user or device.name or "Unnamed device",
                id=device_id,
                info=f"{words(since, exact)} · {_plural(len(rows), 'entity', 'entities')}",
                link=f"/config/devices/device/{device_id}",
                fix="disable",
                since=since.isoformat(),
                or_earlier=not exact,
                parts=len(rows),
            )
        )
    for entity_id, entry, since, exact in lone:
        key = f"unavailable:{entity_id}"
        if key in keep:
            continue
        items.append(
            Item(
                key=key,
                name=_entity_name(hass, entry, entity_id),
                id=entity_id,
                info=f"{words(since, exact)}.",
                link="/config/entities",
                since=since.isoformat(),
                or_earlier=not exact,
            )
        )
    if not items:
        return []
    for item in items:
        if item.key.startswith("unavailable:"):
            users = used_by(hass, [item.id], None)
        else:
            mine = [r[0] for r in by_device.get(item.id, [])]
            users = used_by(hass, mine, item.id)
        item.used_n = len(users)
        item.used_by = users[:USED_BY_SHOWN]
    # What an automation waits for comes first: there an offline thing does harm.
    items.sort(key=lambda i: 0 if i.used_n else 1)
    devices = sum(1 for i in items if i.fix == "disable" or i.of)
    others = len(items) - devices
    if devices and not others:
        title = f"{_plural(devices, 'device')} offline for a long time"
    elif devices:
        title = f"{len(items)} devices and entities offline for a long time"
    else:
        title = f"{_plural(others, 'entity', 'entities')} offline for a long time"
    return [
        Finding(
            kind="unavailable",
            title=title,
            detail="The device may be off, unplugged or out of range. If it is gone for good, disable or remove it.",
            link="/config/entities" if others else "/config/devices/dashboard",
            items=items,
        )
    ]


# ---- 5. Automations and scripts that point to missing things -------------------------------------------------


def _missing_entity(hass: HomeAssistant, ent_reg: er.EntityRegistry, entity_id: str) -> bool:
    # sun.sun is how Home Assistant writes a sunrise or sunset trigger; it works without a Sun entity.
    if "." not in entity_id or "{" in entity_id or entity_id in ("all", "none", "sun.sun"):
        return False
    return hass.states.get(entity_id) is None and ent_reg.async_get(entity_id) is None


def _all_devices(dev_reg: dr.DeviceRegistry) -> list:
    """Every device entry. Newer Home Assistant gives the entries when you go through the list; older gives ids."""
    devices = dev_reg.devices
    return [d if hasattr(d, "disabled_by") else devices[d] for d in list(devices)]


def _device_entry_ids(device: Any) -> list[str]:
    """The integrations (config entries) a device belongs to: one on newer Home Assistant, a set on older."""
    one = getattr(device, "config_entry_id", None)
    if one:
        return [one]
    return [e for e in (getattr(device, "config_entries", None) or ()) if e]


def _object_words(entity_id: str) -> str:
    return entity_id.split(".", 1)[-1].replace("_", " ").strip().lower()


def suggest_new(hass: HomeAssistant, ent_reg: er.EntityRegistry, old: str) -> tuple[str, str]:
    """The entity that looks like the new name of a removed one, or ("", "") when there is no single clear match.

    Integrations sometimes give an entity a new id after an update (ESPHome did: living_room_motion became
    konnected_dc4f22199cf2_living_room_motion). Clues, in order: the same integration and a name that ends the
    same, then any entity of the same kind whose id ends with the old one. Only one match counts.
    """
    domain, _, obj = old.partition(".")
    deleted = next((d for d in ent_reg.deleted_entities.values() if d.entity_id == old), None)
    words = _object_words(old)
    candidates: list[er.RegistryEntry] = []
    for entry in ent_reg.entities.values():
        if entry.domain != domain or entry.entity_id == old or entry.disabled_by is not None:
            continue
        if hass.states.get(entry.entity_id) is None:
            continue
        same_home = deleted is None or entry.platform == deleted.platform
        name = (entry.name or entry.original_name or "").strip().lower()
        if same_home and (entry.entity_id.endswith("_" + obj) or (name and name == words)):
            candidates.append(entry)
    if len(candidates) != 1:
        return "", ""
    entry = candidates[0]
    state = hass.states.get(entry.entity_id)
    return entry.entity_id, str(state.attributes.get(ATTR_FRIENDLY_NAME) or entry.name or entry.original_name or entry.entity_id)


def gone_integration(hass: HomeAssistant, ent_reg: er.EntityRegistry, old: str) -> tuple[str, str]:
    """When the entity's whole integration was removed: its name and when. ("", "") otherwise."""
    deleted = next((d for d in ent_reg.deleted_entities.values() if d.entity_id == old), None)
    if deleted is None:
        return "", ""
    if deleted.config_entry_id:
        if hass.config_entries.async_get_entry(deleted.config_entry_id) is not None:
            return "", ""
    elif deleted.orphaned_timestamp is None:  # Home Assistant marks it orphaned when its integration is removed
        return "", ""
    when = deleted.orphaned_timestamp or deleted.modified_at.timestamp()
    return integration_name(hass, deleted.platform), dt_util.utc_from_timestamp(when).isoformat()


_NESTED_STEPS = ("sequence", "then", "else", "default", "parallel")


def _mentions(value: Any, entity_id: str) -> bool:
    return re.search(rf"(?<![\w.]){re.escape(entity_id)}(?![\w])", json.dumps(value, default=str)) is not None


def _drop_from(holder: dict[str, Any], entity_id: str) -> bool:
    """Take the entity out of holder["entity_id"]. True when it was there."""
    value = holder.get("entity_id")
    ids = [v.strip() for v in value.split(",")] if isinstance(value, str) else list(value) if isinstance(value, list) else None
    if not ids or entity_id not in ids:
        return False
    rest = [v for v in ids if v != entity_id]
    if rest:
        holder["entity_id"] = rest if isinstance(value, list) or len(rest) > 1 else rest[0]
    else:
        del holder["entity_id"]
    return True


def _steps_without(steps: Any, entity_id: str) -> list | None:
    """A list of steps without the ones that only act on the entity. None when a step cannot be taken out cleanly."""
    if isinstance(steps, dict):
        steps = [steps]
    if not isinstance(steps, list):
        return None
    out: list = []
    for step in steps:
        if not isinstance(step, dict) or not _mentions(step, entity_id):
            out.append(step)
            continue
        step = json.loads(json.dumps(step, default=str))
        if "action" in step or "service" in step:
            # A plain service call: take the entity out of its targets. With no target left, the step goes.
            holders = [h for h in (step, step.get("target"), step.get("data")) if isinstance(h, dict)]
            had = [_drop_from(h, entity_id) for h in holders]
            if not any(had):
                return None
            if isinstance(step.get("target"), dict) and not step["target"]:
                del step["target"]
            aims = any(k in h for h in holders for k in ("entity_id", "device_id", "area_id", "floor_id", "label_id"))
            if aims:
                out.append(step)
            continue
        changed = False
        for key in _NESTED_STEPS:
            if key in step and _mentions(step[key], entity_id):
                inner = _steps_without(step[key], entity_id)
                if not inner:  # an emptied branch would change what the automation means
                    return None
                step[key] = inner
                changed = True
        if isinstance(step.get("repeat"), dict) and _mentions(step["repeat"].get("sequence"), entity_id):
            inner = _steps_without(step["repeat"]["sequence"], entity_id)
            if not inner:
                return None
            step["repeat"]["sequence"] = inner
            changed = True
        if isinstance(step.get("choose"), list):
            for option in step["choose"]:
                if isinstance(option, dict) and _mentions(option.get("sequence"), entity_id):
                    inner = _steps_without(option["sequence"], entity_id)
                    if not inner:
                        return None
                    option["sequence"] = inner
                    changed = True
        if not changed:
            return None
        out.append(step)
    return out


def without_entity(config: Any, entity_id: str) -> dict[str, Any] | None:
    """The automation without the steps that act on a missing entity, or None when that is not a clean cut.

    Only plain steps are removed (a service call aimed at the entity). When the entity is also in a trigger,
    a condition or a template, or when no step would be left, the answer is None and no fix is offered.
    """
    if not isinstance(config, dict):
        return None
    key = "actions" if "actions" in config else "action" if "action" in config else None
    if key is None:
        return None
    after = json.loads(json.dumps(config, default=str))
    steps = _steps_without(after[key], entity_id)
    if not steps:
        return None
    after[key] = steps
    if _mentions(after, entity_id) or after == config:
        return None
    return after


def _automation_config(hass: HomeAssistant, entity_id: str) -> dict[str, Any] | None:
    """The automation as it was written, read from memory."""
    try:
        from homeassistant.components.automation import DATA_COMPONENT

        entity = hass.data[DATA_COMPONENT].get_entity(entity_id)
        raw = getattr(entity, "raw_config", None)
        return dict(raw) if raw else None
    except Exception:  # noqa: BLE001
        return None


@callback
def check_broken_references(
    hass: HomeAssistant, keep: frozenset[str] = frozenset(), facts: YamlFacts | None = None
) -> list[Finding]:
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    items: list[Item] = []
    sources = []
    try:
        from homeassistant.components import automation

        sources.append(("automation", automation.entities_in_automation, automation.devices_in_automation))
    except ImportError:
        pass
    try:
        from homeassistant.components import script

        sources.append(("script", script.entities_in_script, script.devices_in_script))
    except ImportError:
        pass
    for domain, entities_in, devices_in in sources:
        if domain not in hass.config.components:
            continue
        for owner_id in hass.states.async_entity_ids(domain):
            # An automation that is switched off cannot fail, so its old steps are not a problem today.
            if domain == "automation" and (owner_state := hass.states.get(owner_id)) and owner_state.state == "off":
                continue
            try:
                missing = [e for e in entities_in(hass, owner_id) if _missing_entity(hass, ent_reg, e)]
                missing += [
                    f"a removed device ({d[:8]})" for d in devices_in(hass, owner_id) if dev_reg.async_get(d) is None
                ]
            except Exception:  # noqa: BLE001 - one odd automation must not stop the checkup
                continue
            if not missing:
                continue
            state = hass.states.get(owner_id)
            name = _entity_name(hass, ent_reg.async_get(owner_id), owner_id)
            link = "/config/automation/dashboard" if domain == "automation" else "/config/script/dashboard"
            if domain == "automation" and state and state.attributes.get("id"):
                link = f"/config/automation/edit/{state.attributes['id']}"
            elif domain == "script":
                link = f"/config/script/edit/{owner_id.split('.', 1)[1]}"
            last = state.attributes.get("last_triggered") if state else None
            last_ran = last.isoformat() if hasattr(last, "isoformat") else str(last or "")
            # Home Assistant's editor can change only what is in automations.yaml and scripts.yaml. Anything written
            # in another YAML file (a package, an included folder) gets no button: the line says where it is instead.
            editable = facts is None or facts.editable(domain, owner_id, state)
            can_fix = domain == "automation" and state is not None and bool(state.attributes.get("id")) and editable
            for target in missing:
                item = Item(
                    key=f"ref:{owner_id}:{target}",
                    name=name,
                    id=owner_id,
                    info=f"Points to {target}, which no longer exists.",
                    link=link,
                    last_ran=last_ran,
                )
                if not target.startswith("a removed device"):
                    item.old = target
                    new_id, new_name = suggest_new(hass, ent_reg, target)
                    gone, gone_at = gone_integration(hass, ent_reg, target)
                    if new_id:
                        item.to, item.to_name = new_id, new_name
                        item.info = f"Points to {target}, which no longer exists. {new_name} looks like its new name."
                        item.fix = "use_new" if can_fix else ""
                    else:
                        if gone:
                            item.gone, item.gone_at = gone, gone_at
                            item.info = f"{gone} was removed, so this step can never work."
                        # The rest of the automation still works: offer to take out only the broken step.
                        if can_fix and without_entity(_automation_config(hass, owner_id), target) is not None:
                            item.fix = "remove_step"
                        elif gone and domain == "automation":
                            item.fix = "turn_off"
                        # No safe fix by itself: the person can choose what the step should use now. Scripts too.
                        if not item.fix and (can_fix or (domain == "script" and editable)) and "." in target:
                            item.choose = True
                    if not editable and facts is not None and item.key in facts.spots:
                        item.file, item.line = facts.spots[item.key]
                else:
                    device_id = target.rsplit("(", 1)[-1].rstrip(")")
                    deleted_dev = next((d for i, d in dev_reg.deleted_devices.items() if i.startswith(device_id)), None)
                    if deleted_dev is not None and not _device_entry_ids(deleted_dev) and domain == "automation":
                        item.fix = "turn_off"
                        when = getattr(deleted_dev, "orphaned_timestamp", None) or deleted_dev.modified_at.timestamp()
                        item.gone_at = dt_util.utc_from_timestamp(when).isoformat()
                items.append(item)
    items = [i for i in items if i.key not in keep]
    if not items:
        return []
    # Still-running automations first: they are the ones quietly failing today.
    items.sort(key=lambda i: i.last_ran or "", reverse=True)
    owners = len({i.id for i in items})
    return [
        Finding(
            kind="broken_references",
            title=f"{_plural(owners, 'automation or script', 'automations and scripts')} {'points' if owners == 1 else 'point'} to missing things",
            detail="These steps will fail when they run. Open each one and pick the new device or entity.",
            link="/config/automation/dashboard",
            items=items,
        )
    ]


# ---- 5b. Where a hand-written automation or script lives -----------------------------------------------------


@dataclass
class YamlFacts:
    """What the YAML files say about automations and scripts. Read in a worker thread; only names and line numbers."""

    scripts: frozenset[str] = frozenset()  # the scripts in scripts.yaml: the ones Home Assistant's editor can change
    automations: frozenset[str] = frozenset()  # the automation ids in automations.yaml
    spots: dict[str, tuple[str, int]] = field(default_factory=dict)  # item key -> (file, line) of the missing entity

    def editable(self, domain: str, owner_id: str, state: Any) -> bool:
        if domain == "script":
            return owner_id.split(".", 1)[1] in self.scripts
        return bool(state and str(state.attributes.get("id") or "") in self.automations)


_SCRIPT_KEY = re.compile(r"^([A-Za-z0-9_]+):", re.MULTILINE)
_AUTOMATION_ID = re.compile(r"""^(?:-\s+| {0,2})id:\s*['"]?([^'"\s#]+)""", re.MULTILINE)


def broken_refs(hass: HomeAssistant) -> list[tuple[str, str, list[str]]]:
    """(item key, missing entity, words that mark its owner in a YAML file) for every broken step."""
    refs: list[tuple[str, str, list[str]]] = []
    for finding in check_broken_references(hass):
        for item in finding.items:
            if not item.old:
                continue
            domain, object_id = item.id.split(".", 1)
            if domain == "script":
                marks = [rf"^\s*{re.escape(object_id)}:\s*(#.*)?$"]
            else:
                state = hass.states.get(item.id)
                marks = [rf"""^\s*-?\s*alias:\s*['"]?{re.escape(item.name)}['"]?\s*$"""]
                if state and state.attributes.get("id"):
                    marks.append(rf"""^\s*-?\s*id:\s*['"]?{re.escape(str(state.attributes['id']))}['"]?\s*$""")
            refs.append((item.key, item.old, marks))
    return refs


def _yaml_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in CORPUS_SKIP_DIRS and not d.startswith(".")]
        for filename in sorted(filenames):
            lower = filename.lower()
            if lower.endswith((".yaml", ".yml")) and not any(part in lower for part in CORPUS_SKIP_NAME_PARTS):
                yield Path(dirpath) / filename


def read_yaml_facts(config_dir: str, refs: list[tuple[str, str, list[str]]]) -> YamlFacts:
    """Which automations and scripts the editor can change, and where the broken steps of the others are written.

    Runs in a worker thread. Keeps only script names, automation ids, file names and line numbers.
    """
    root = Path(config_dir)

    def text_of(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore") if path.stat().st_size <= CORPUS_MAX_BYTES else ""
        except OSError:
            return ""

    facts = YamlFacts(
        scripts=frozenset(_SCRIPT_KEY.findall(text_of(root / "scripts.yaml"))),
        automations=frozenset(_AUTOMATION_ID.findall(text_of(root / "automations.yaml"))),
    )
    if not refs:
        return facts
    wanted = [
        (key, old, re.compile(rf"(?<![\w.]){re.escape(old)}(?!\w)"), [re.compile(m) for m in marks])
        for key, old, marks in refs
    ]
    # For each broken step: the place nearest below its owner's name. (distance, file, line)
    best: dict[str, tuple[int, str, int]] = {}
    seen: dict[str, list[tuple[str, int]]] = {}
    for path in _yaml_files(root):
        text = text_of(path)
        if not any(old in text for _key, old, _token, _marks in wanted):
            continue
        lines = text.splitlines()
        name = path.relative_to(root).as_posix()
        for key, old, token, marks in wanted:
            if old not in text:
                continue
            for number, line in enumerate(lines):
                if old not in line or not token.search(line) or line.lstrip().startswith("#"):
                    continue
                seen.setdefault(key, []).append((name, number + 1))
                for back in range(number, -1, -1):
                    if any(mark.match(lines[back]) for mark in marks):
                        if key not in best or number - back < best[key][0]:
                            best[key] = (number - back, name, number + 1)
                        break
    for key, _old, _token, _marks in wanted:
        if key in best:
            facts.spots[key] = best[key][1:]
        elif len(seen.get(key, [])) == 1:
            facts.spots[key] = seen[key][0]
    return facts


# ---- 6. Helpers nothing seems to use ------------------------------------------------------------------------


def read_corpus(config_dir: str) -> set[str]:
    """Every helper id written anywhere in the YAML files and the dashboard storage. Runs in a worker thread.

    Only helper ids are picked out; the rest of the text is dropped at once. Secret files are never opened.
    """
    found: set[str] = set()
    budget = CORPUS_MAX_BYTES
    root = Path(config_dir)

    def take(path: Path) -> None:
        nonlocal budget
        try:
            size = path.stat().st_size
            if size > budget:
                return
            budget -= size
            found.update(_HELPER_ID.findall(path.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            return

    for path in _yaml_files(root):
        take(path)
    storage = root / ".storage"
    if storage.is_dir():
        for path in storage.iterdir():
            if path.name.startswith(CORPUS_STORAGE_PREFIXES):
                take(path)
    return found


@callback
def check_unused_helpers(hass: HomeAssistant, corpus: set[str] | None, keep: frozenset[str] = frozenset()) -> list[Finding]:
    if corpus is None:
        return []
    ent_reg = er.async_get(hass)
    now = dt_util.utcnow()
    used: set[str] = set(corpus) | helpers_in_template_settings(hass)
    for domain, getter in _reference_getters(hass):
        for owner_id in hass.states.async_entity_ids(domain):
            try:
                used.update(getter(hass, owner_id))
            except Exception:  # noqa: BLE001
                continue
    items: list[Item] = []
    for entity_id in hass.states.async_entity_ids(HELPER_DOMAINS):
        if entity_id in used:
            continue
        entry = ent_reg.async_get(entity_id)
        created = getattr(entry, "created_at", None)
        if created is not None and now - created < HELPER_MIN_AGE:
            continue
        items.append(
            Item(
                key=f"helper:{entity_id}",
                name=_entity_name(hass, entry, entity_id),
                id=entity_id,
                info="No automation, script, dashboard or template mentions it.",
                link="/config/helpers",
            )
        )
    items = [i for i in items if i.key not in keep]
    if not items:
        return []
    return [
        Finding(
            kind="unused_helpers",
            title=f"{_plural(len(items), 'helper')} nothing seems to use",
            detail="Something outside Home Assistant (like Node-RED) may still use them. Mark those as Ignore.",
            severity="info",
            link="/config/helpers",
            items=items,
        )
    ]


@callback
def helpers_in_template_settings(hass: HomeAssistant) -> set[str]:
    """Helpers named in the settings of template-style helpers (made in the UI). Read in memory, options only."""
    found: set[str] = set()
    for domain in TEMPLATE_HELPER_DOMAINS:
        for entry in hass.config_entries.async_entries(domain):
            try:
                found.update(_HELPER_ID.findall(json.dumps(dict(entry.options), default=str)))
            except (TypeError, ValueError):
                continue
    return found


def _reference_getters(hass: HomeAssistant) -> list:
    out = []
    try:
        from homeassistant.components import automation

        if "automation" in hass.config.components:
            out.append(("automation", automation.entities_in_automation))
    except ImportError:
        pass
    try:
        from homeassistant.components import script

        if "script" in hass.config.components:
            out.append(("script", script.entities_in_script))
    except ImportError:
        pass
    return out


# ---- 7. Batteries running low ----------------------------------------------------------------------------------


# Phones, tablets and computers report their battery through these integrations. People charge them; they do not
# change their batteries, and a sleeping laptop often reports an old, low number. They are left out.
_CHARGED_DEVICE_PLATFORMS = frozenset({"mobile_app", "icloud", "icloud3", "ios", "kdeconnect", "hass_agent"})


@callback
def check_batteries(hass: HomeAssistant, keep: frozenset[str] = frozenset()) -> list[Finding]:
    """Batteries under 15%, or a "battery low" sensor that is on, so they can be changed before they die."""
    dev_reg = dr.async_get(hass)
    ent_reg = er.async_get(hass)
    items: list[Item] = []
    for state in hass.states.async_all(("sensor", "binary_sensor")):
        if state.attributes.get("device_class") != "battery":
            continue
        level = ""
        if state.domain == "sensor":
            if state.attributes.get("unit_of_measurement") != "%":
                continue
            try:
                value = float(state.state)
            except ValueError:
                continue
            if value >= BATTERY_LOW:
                continue
            level = f"{round(value)}%"
        elif state.state != "on":
            continue
        entry = ent_reg.async_get(state.entity_id)
        if entry and entry.platform in _CHARGED_DEVICE_PLATFORMS:
            continue
        device = dev_reg.async_get(entry.device_id) if entry and entry.device_id else None
        name = (device.name_by_user or device.name) if device else None
        items.append(
            Item(
                key=f"battery:{state.entity_id}",
                name=name or _entity_name(hass, entry, state.entity_id),
                id=state.entity_id,
                info=f"Battery at {level}" if level else "Battery low",
                link=f"/config/devices/device/{device.id}" if device else "/config/entities",
            )
        )
    items = [i for i in items if i.key not in keep]
    if not items:
        return []
    items.sort(key=lambda i: (i.info != "Battery low", float(i.info.split()[-1].rstrip("%")) if "%" in i.info else 0))
    return [
        Finding(
            kind="low_batteries",
            title=_plural(len(items), "battery", "batteries") + " running low",
            detail="Change them before the device stops working.",
            link="/config/devices/dashboard",
            items=items,
        )
    ]


# ---- 8. Updates worth reading first -------------------------------------------------------------------------------

_NOT_BREAKING = re.compile(r"\b(no|non|not|without|zero)[ -]+(known[ -]+)?breaking", re.I)
_BREAKING = re.compile(
    r"breaking|backwards?[ -]incompatible|not backwards?[ -]compatible|migration (is )?(required|needed)|"
    r"action (is )?required|you (must|need to|have to) (re-?configure|re-?add|re-?install|change|update your)",
    re.I,
)
NOTES_MAX = 20000


async def read_update_notes(hass: HomeAssistant, known: dict[str, list[str]]) -> dict[str, list[str]]:
    """The release notes of waiting updates, asked from Home Assistant's own update entities, once per version.

    This is what Home Assistant shows when you open an update. Nothing about the home is sent anywhere.
    """
    out: dict[str, list[str]] = {}
    component = hass.data.get("update")
    for state in hass.states.async_all("update"):
        if state.state != "on":
            continue
        latest = str(state.attributes.get("latest_version") or "")
        old = known.get(state.entity_id)
        if old and old[0] == latest:
            out[state.entity_id] = old
            continue
        text = ""
        try:
            entity = component.get_entity(state.entity_id) if component is not None else None
            if entity is not None and int(entity.supported_features or 0) & 16:  # UpdateEntityFeature.RELEASE_NOTES
                text = str(await asyncio.wait_for(entity.async_release_notes(), 20) or "")
        except Exception:  # noqa: BLE001 - without notes the summary is still read
            _LOGGER.debug("Could not read the release notes of %s", state.entity_id, exc_info=True)
        out[state.entity_id] = [latest, text[:NOTES_MAX]]
    return out


def _major(version: str) -> int | None:
    match = re.match(r"v?(\d+)\.", version.strip())
    number = int(match.group(1)) if match else None
    return None if number is None or number >= 1000 else number  # 2026.11 is a date, not a big step


@callback
def check_updates(
    hass: HomeAssistant, keep: frozenset[str] = frozenset(), notes: dict[str, list[str]] | None = None
) -> list[Finding]:
    """Waiting updates to read before installing: their notes mention a breaking change, or the version jumps.

    Routine updates are not listed. Home Assistant already shows those.
    """
    notes = notes or {}
    items: list[Item] = []
    for state in hass.states.async_all("update"):
        if state.state != "on" or state.attributes.get("in_progress") not in (None, False):
            continue
        installed = str(state.attributes.get("installed_version") or "")
        latest = str(state.attributes.get("latest_version") or "")
        if not latest or state.attributes.get("skipped_version") == latest:
            continue
        noted = notes.get(state.entity_id)
        text = f"{state.attributes.get('release_summary') or ''}\n{noted[1] if noted and noted[0] == latest else ''}"
        risk = ""
        if _BREAKING.search(_NOT_BREAKING.sub(" ", text)):
            risk = "breaking"
        else:
            before, after = _major(installed), _major(latest)
            if before is not None and after is not None and after > before:
                risk = "major"
        if not risk:
            continue
        name = str(state.attributes.get("title") or state.attributes.get(ATTR_FRIENDLY_NAME) or state.entity_id)
        items.append(
            Item(
                key=f"update:{state.entity_id}:{latest}",
                name=re.sub(r"\s+update$", "", name, flags=re.I),
                id=state.entity_id,
                info=f"{installed} → {latest}" if installed else latest,
                link="/config/updates",
                risk=risk,
            )
        )
    items = [i for i in items if i.key not in keep]
    if not items:
        return []
    items.sort(key=lambda i: (i.risk != "breaking", i.name.lower()))
    return [
        Finding(
            kind="updates",
            title=f"{_plural(len(items), 'update')} to read before you install",
            detail="Their notes mention a breaking change, or the version makes a big step.",
            severity="info",
            link="/config/updates",
            items=items,
        )
    ]


# ---- 9. Devices that could have an area ---------------------------------------------------------------------------


def _words(text: str) -> str:
    return " ".join(re.sub(r"[^\w]+", " ", (text or "").lower()).split())


@callback
def check_areas(hass: HomeAssistant, keep: frozenset[str] = frozenset()) -> list[Finding]:
    """Devices without an area whose own name says where they are ("Kitchen Echo" and the area "Kitchen").

    Only a clear match is suggested: the longest area name in the device name, and only one of that length.
    """
    dev_reg = dr.async_get(hass)
    ent_reg = er.async_get(hass)
    areas = sorted(
        ((_words(a.name), a) for a in ar.async_get(hass).async_list_areas() if len(_words(a.name)) >= 3),
        key=lambda pair: -len(pair[0]),
    )
    if not areas:
        return []
    items: list[Item] = []
    for device in dev_reg.devices.values():
        if device.area_id or device.disabled_by is not None or device.entry_type is dr.DeviceEntryType.SERVICE:
            continue
        key = f"area:{device.id}"
        if key in keep:
            continue
        name = device.name_by_user or device.name or ""
        padded = f" {_words(name)} "
        hits = [(words, area) for words, area in areas if f" {words} " in padded]
        if not hits or (len(hits) > 1 and len(hits[1][0]) == len(hits[0][0])):
            continue
        if not any(e.disabled_by is None for e in er.async_entries_for_device(ent_reg, device.id)):
            continue
        area = hits[0][1]
        items.append(
            Item(
                key=key,
                name=name,
                id=device.id,
                info=f"Suggested area: {area.name}",
                link=f"/config/devices/device/{device.id}",
                fix="set_area",
                to=area.id,
                to_name=area.name,
            )
        )
    if not items:
        return []
    items.sort(key=lambda i: (i.to_name.lower(), i.name.lower()))
    return [
        Finding(
            kind="areas",
            title=f"{_plural(len(items), 'device')} could have an area",
            detail="Their name says where they are. A device with an area shows up in the right room.",
            severity="info",
            link="/config/devices/dashboard",
            items=items,
        )
    ]


# ---- All together ---------------------------------------------------------------------------------------------


def checked_counts(hass: HomeAssistant) -> dict[str, int]:
    """How much each check looked at, so a green mark on the page can say what stands behind it. Only counts."""
    ent_reg = er.async_get(hass)
    batteries = 0
    for state in hass.states.async_all(("sensor", "binary_sensor")):
        if state.attributes.get("device_class") != "battery":
            continue
        if state.domain == "sensor" and state.attributes.get("unit_of_measurement") != "%":
            continue
        entry = ent_reg.async_get(state.entity_id)
        if entry and entry.platform in _CHARGED_DEVICE_PLATFORMS:
            continue
        batteries += 1
    return {
        "integrations": len(hass.config_entries.async_entries()),
        "automations": len(hass.states.async_entity_ids(("automation", "script"))),
        "entities": len(ent_reg.entities),
        "devices": len(_all_devices(dr.async_get(hass))),
        "states": len(hass.states.async_entity_ids()),
        "helpers": len(hass.states.async_entity_ids(HELPER_DOMAINS)),
        "batteries": batteries,
    }


# ---- 10. Automations that never run -------------------------------------------------------------------------


@callback
def check_idle_automations(hass: HomeAssistant, keep: frozenset[str] = frozenset()) -> list[Finding]:
    """Automations that are switched on but never ran, or did not run for a long time. Shown, not counted.

    Some are seasonal (holiday lights), so this is a quiet list with "Ignore", never an alarm.
    """
    now = dt_util.utcnow()
    ent_reg = er.async_get(hass)
    items: list[Item] = []
    for state in hass.states.async_all("automation"):
        if state.state != "on" or state.attributes.get(ATTR_RESTORED):
            continue
        key = f"idle:{state.entity_id}"
        if key in keep:
            continue
        last = state.attributes.get("last_triggered")
        if isinstance(last, str):
            last = dt_util.parse_datetime(last)
        entry = ent_reg.async_get(state.entity_id)
        if last is None:
            # A new automation has had no chance yet. Without a known age, we say nothing.
            created = getattr(entry, "created_at", None) if entry else None
            if created is None or created.timestamp() <= 0 or now - created < IDLE_NEW:
                continue
        elif now - last < IDLE_AFTER:
            continue
        auto_id = state.attributes.get("id")
        waits = waits_for(hass, state.entity_id)
        items.append(
            Item(
                key=key,
                name=str(state.attributes.get(ATTR_FRIENDLY_NAME) or state.entity_id),
                id=state.entity_id,
                info="Never ran" if last is None else f"Last ran {dt_util.as_local(last).strftime('%-d %b %Y')}",
                link=f"/config/automation/edit/{auto_id}" if auto_id else "/config/automation/dashboard",
                last_ran=last.isoformat() if last else "",
                # One story from two lists: it does not run because what it waits for is offline.
                hint="waits" if waits else "",
                device=waits,
            )
        )
    if not items:
        return []
    items.sort(key=lambda i: (i.hint != "waits", i.last_ran != "", i.last_ran, i.name.lower()))
    return [
        Finding(
            kind="idle_automations",
            title=f"{_plural(len(items), 'automation')} did not run for a long time",
            detail="Switched on, but it did not run for 90 days or more. Its trigger may be broken, or it is no longer needed.",
            severity="info",
            link="/config/automation/dashboard",
            items=items,
        )
    ]


@callback
def waits_for(hass: HomeAssistant, automation_id: str) -> str:
    """The name of an offline thing this automation uses, or "". A device counts when nothing of it works."""
    try:
        from homeassistant.components import automation  # noqa: PLC0415

        entities = automation.entities_in_automation(hass, automation_id)
        devices = automation.devices_in_automation(hass, automation_id)
    except Exception:  # noqa: BLE001
        return ""
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    for device_id in devices:
        device = dev_reg.async_get(device_id)
        if device is not None and er.async_entries_for_device(ent_reg, device_id) and _down(hass, ent_reg, device_id):
            return device.name_by_user or device.name or ""
    for entity_id in entities:
        state = hass.states.get(entity_id)
        if state is None or state.state != STATE_UNAVAILABLE:
            continue
        entry = ent_reg.async_get(entity_id)
        device = dev_reg.async_get(entry.device_id) if entry and entry.device_id else None
        if device is not None and _down(hass, ent_reg, device.id):
            return device.name_by_user or device.name or _entity_name(hass, entry, entity_id)
        return _entity_name(hass, entry, entity_id)
    return ""


# ---- 11. Backup age -------------------------------------------------------------------------------------------


async def read_backup(hass: HomeAssistant) -> dict[str, Any] | None:
    """When the newest backup was made, from Home Assistant's own backup list. None: backups are not set up here.

    Every backup counts, also one made by hand or by an add-on. Only dates are read, never the content.
    """
    if "backup" not in hass.config.components:
        return None
    from homeassistant.components.backup import async_get_manager  # noqa: PLC0415

    backups, _errors = await async_get_manager(hass).async_get_backups()
    dates = [d for d in (dt_util.parse_datetime(str(b.date)) for b in backups.values()) if d is not None]
    return {"last": max(dates).timestamp() if dates else None}


@callback
def check_backup(hass: HomeAssistant, keep: frozenset[str] = frozenset(), backup: dict[str, Any] | None = None) -> list[Finding]:
    if backup is None or "backup:old" in keep:
        return []
    # Home Assistant tells about a failed backup itself (Repairs). Then we do not say it a second time.
    if any(i.domain == "backup" and i.active and not i.dismissed_version for i in ir.async_get(hass).issues.values()):
        return []
    last = backup.get("last")
    now = time.time()
    if last is not None and now - last < BACKUP_OLD.total_seconds():
        return []
    return [
        Finding(
            kind="backup",
            title="There is no backup yet" if last is None else "The last backup is old",
            detail="A fresh backup lets you go back when an update goes wrong.",
            link="/config/backup",
            items=[
                Item(
                    key="backup:old",
                    name="Backup",
                    id="backup",
                    info="No backup yet" if last is None else f"Last backup {_day(last)}",
                    link="/config/backup",
                    since=dt_util.utc_from_timestamp(last).isoformat() if last else "",
                    hint="nobackup" if last is None else "oldbackup",
                )
            ],
        )
    ]


def _day(when: float) -> str:
    return dt_util.as_local(dt_util.utc_from_timestamp(when)).strftime("%-d %b")


# ---- 12. Storage ----------------------------------------------------------------------------------------------

_GB = 1024**3


def read_storage(config_dir: str) -> dict[str, float] | None:
    """How full the storage is, and how big the history database is. Runs outside the event loop. Only sizes."""
    import shutil  # noqa: PLC0415

    try:
        usage = shutil.disk_usage(config_dir)
    except OSError:
        return None
    database = 0
    for name in ("home-assistant_v2.db", "home-assistant_v2.db-wal"):
        try:
            database += os.path.getsize(os.path.join(config_dir, name))
        except OSError:
            pass
    return {"total": float(usage.total), "used": float(usage.total - usage.free), "free": float(usage.free), "database": float(database)}


def note_storage(samples: list[list[float]], storage: dict[str, float] | None, now: float) -> None:
    """Keep one reading of the used space per half day, for a month. From these the page can say how fast it fills."""
    if storage is None:
        return
    if not samples or now - samples[-1][0] >= 12 * 3600:
        samples.append([now, storage["used"]])
    del samples[:-60]


@callback
def check_storage(
    keep: frozenset[str] = frozenset(),
    storage: dict[str, float] | None = None,
    samples: list[list[float]] | None = None,
    now: float | None = None,
) -> list[Finding]:
    if not storage or storage["total"] <= 0:
        return []
    now = now if now is not None else time.time()
    total, used, free = storage["total"], storage["used"], storage["free"]
    items: list[Item] = []
    full = used / total >= STORAGE_FULL
    if full:
        items.append(Item(key="storage:full", name="Storage", id="storage", hint="storagefull",
                          info=f"{free / _GB:.1f} GB free of {total / _GB:.0f} GB", link="/config/storage",
                          amount=round(free / _GB, 1), total=round(total / _GB)))
    else:
        # Not full yet, but filling: say when, so there is time to act. Needs at least 3 days of readings.
        old = next((s for s in (samples or []) if now - s[0] >= 3 * 86400), None)
        first = (samples or [None])[0]
        if old is not None and first is not None and now > first[0]:
            per_day = (used - first[1]) / ((now - first[0]) / 86400)
            if per_day > 0 and free / per_day <= STORAGE_SOON_DAYS:
                days = max(1, int(free / per_day))
                items.append(Item(key="storage:filling", name="Storage", id="storage", hint="storagefilling",
                                  info=f"Full in about {_plural(days, 'day')} at this rate", link="/config/storage",
                                  amount=round(free / _GB, 1), total=round(total / _GB), days=days))
    counted = bool(items)
    database = storage.get("database", 0)
    if database >= DATABASE_BIG or (database >= _GB and database >= 0.25 * total):
        items.append(Item(key="storage:database", name="History database", id="recorder", hint="bigdatabase",
                          info=f"{database / _GB:.1f} GB", link="/config/storage", amount=round(database / _GB, 1),
                          total=round(total / _GB)))
    items = [i for i in items if i.key not in keep]
    if not items:
        return []
    counted = counted and any(i.key != "storage:database" for i in items)
    return [
        Finding(
            kind="storage",
            title="The storage is almost full" if full and counted else "The storage is filling up" if counted else "The history database is big",
            detail="When the storage is full, Home Assistant stops recording and updates fail.",
            severity="warning" if counted else "info",
            link="/config/storage",
            items=items,
        )
    ]


# ---- 13. What fills the history -----------------------------------------------------------------------------


class ChangeCounter:
    """Counts how often each entity changes. Two half-day windows, so the picture stays fresh.

    Only counts are kept, never values. `dump` and `load` carry the counts over a restart of Home Assistant.
    """

    KEPT = 300  # the busiest entities per window that are saved; the calm ones do not matter here

    def __init__(self) -> None:
        self.now: dict[str, int] = {}
        self.before: dict[str, int] = {}
        self.started = time.time()
        self.turned = self.started

    def add(self, entity_id: str) -> None:
        self.now[entity_id] = self.now.get(entity_id, 0) + 1

    def turn(self, now: float) -> None:
        if now - self.turned >= 12 * 3600:
            self.before, self.now, self.turned = self.now, {}, now
            self.started = max(self.started, now - 24 * 3600)

    def hours(self, now: float) -> float:
        return (now - self.started) / 3600

    def dump(self, now: float) -> dict[str, Any]:
        def top(counts: dict[str, int]) -> dict[str, int]:
            return dict(sorted(counts.items(), key=lambda kv: -kv[1])[: self.KEPT])

        return {"now": top(self.now), "before": top(self.before), "started": self.started, "turned": self.turned, "saved": now}

    def load(self, data: dict[str, Any] | None, now: float) -> None:
        """Take over the counts from before a restart. The time Home Assistant was off is not counted."""
        try:
            saved = float(data["saved"])
            started, turned = float(data["started"]), float(data["turned"])
            counts = [{str(k): int(v) for k, v in data[name].items()} for name in ("now", "before")]
        except (KeyError, TypeError, ValueError, AttributeError):
            return
        off = now - saved
        if off < 0 or off > 12 * 3600 or not started <= turned <= saved:
            return  # off for too long (or a changed clock): the old counts say little about today
        for entity_id, count in counts[0].items():
            self.now[entity_id] = self.now.get(entity_id, 0) + count
        self.before = counts[1]
        self.started, self.turned = started + off, turned + off

    def per_day(self, now: float) -> dict[str, float]:
        hours = self.hours(now)
        if hours <= 0:
            return {}
        both = dict(self.before)
        for entity_id, count in self.now.items():
            both[entity_id] = both.get(entity_id, 0) + count
        return {entity_id: count * 24 / hours for entity_id, count in both.items()}


@callback
def check_history(
    hass: HomeAssistant, keep: frozenset[str] = frozenset(), changes: ChangeCounter | None = None, now: float | None = None
) -> list[Finding]:
    """The few entities that write most often to the history. Shown, not counted."""
    now = now if now is not None else time.time()
    if changes is None or changes.hours(now) < CHATTY_MIN_HOURS:
        return []
    recorded = None
    try:
        from homeassistant.components.recorder import get_instance  # noqa: PLC0415

        recorded = get_instance(hass).entity_filter
    except Exception:  # noqa: BLE001 - no recorder here: then nothing fills a history
        return []
    ent_reg = er.async_get(hass)
    limit = 86400 / CHATTY_EVERY
    items: list[Item] = []
    for entity_id, per_day in sorted(changes.per_day(now).items(), key=lambda kv: -kv[1]):
        if per_day < limit or len(items) >= CHATTY_SHOWN:
            break
        key = f"chatty:{entity_id}"
        if key in keep or hass.states.get(entity_id) is None or (recorded is not None and not recorded(entity_id)):
            continue
        every = max(1, round(86400 / per_day))
        items.append(
            Item(
                key=key,
                name=_entity_name(hass, ent_reg.async_get(entity_id), entity_id),
                id=entity_id,
                info=f"Writes about every {_plural(every, 'second')}",
                link="/config/entities",
                hint="chatty",
                every=every,
            )
        )
    if not items:
        return []
    return [
        Finding(
            kind="history",
            title=f"{_plural(len(items), 'entity writes', 'entities write')} to the history very often",
            detail="They fill the history database fastest. If you do not need their history, stop recording them.",
            severity="info",
            link="/config/entities",
            items=items,
        )
    ]


# ---- 14. Weak signal, before it goes offline -----------------------------------------------------------------


@callback
def check_signal(
    hass: HomeAssistant, keep: frozenset[str] = frozenset(), memory: dict[str, float] | None = None, now: float | None = None
) -> list[Finding]:
    """Devices whose own signal reading has been weak for a day or more. Shown, not counted.

    `memory`: entity id -> since when it is weak. One good reading clears it, so a short dip never shows.
    """
    now = now if now is not None else time.time()
    memory = memory if memory is not None else {}
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    weak_now: set[str] = set()
    for state in hass.states.async_all("sensor"):
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            continue
        unit = str(state.attributes.get("unit_of_measurement") or "").lower()
        if state.attributes.get("device_class") == "signal_strength" and unit == "dbm":
            weak = value <= WEAK_RSSI and value < 0
        elif unit == "lqi" or state.entity_id.endswith(("_linkquality", "_lqi")):
            weak = 0 < value <= WEAK_LQI
        else:
            continue
        if weak:
            weak_now.add(state.entity_id)
    for entity_id in list(memory):
        if entity_id not in weak_now:
            del memory[entity_id]
    by_thing: dict[str, tuple[str, float, str]] = {}
    for entity_id in weak_now:
        since = memory.setdefault(entity_id, now)
        if now - since < WEAK_AFTER.total_seconds():
            continue
        entry = ent_reg.async_get(entity_id)
        device = dev_reg.async_get(entry.device_id) if entry and entry.device_id else None
        thing = device.id if device else entity_id
        name = (device.name_by_user or device.name) if device else _entity_name(hass, entry, entity_id)
        link = f"/config/devices/device/{device.id}" if device else "/config/entities"
        if thing not in by_thing or since < by_thing[thing][1]:
            by_thing[thing] = (name or entity_id, since, link)
    items = [
        Item(key=f"signal:{thing}", name=name, id=thing, info=f"Weak signal since {_day(since)}", link=link,
             hint="weaksignal", since=dt_util.utc_from_timestamp(since).isoformat())
        for thing, (name, since, link) in sorted(by_thing.items(), key=lambda kv: kv[1][1])
        if f"signal:{thing}" not in keep
    ]
    if not items:
        return []
    return [
        Finding(
            kind="weak_signal",
            title=f"{_plural(len(items), 'device has', 'devices have')} a weak signal",
            detail="It still works, but it may drop soon.",
            severity="info",
            link="/config/devices/dashboard",
            items=items,
        )
    ]


# ---- 15. Names that confuse voice ----------------------------------------------------------------------------

_ASSISTANTS = ("conversation", "cloud.alexa", "cloud.google_assistant")


@callback
def check_voice_names(hass: HomeAssistant, keep: frozenset[str] = frozenset()) -> list[Finding]:
    """Two things with the same name that a voice assistant can reach. Shown, not counted.

    Assist tells same-named things apart by their area, so there only the same area (or no area) is a clash.
    """
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    # Only the saved choice is read. Asking Home Assistant would make it save a choice, and this check only reads.
    assistants = [a for a in _ASSISTANTS if a == "conversation" or "cloud" in hass.config.components]
    by_name: dict[tuple[str, str], list[tuple[str, str | None]]] = defaultdict(list)
    thing_of: dict[str, str] = {}  # entity -> its device. Two parts of one device (a TV and its remote) are no clash.
    for state in hass.states.async_all():
        if state.domain in ("automation", "script", "scene", "update", "sensor", "binary_sensor", "button", "event"):
            continue
        name = " ".join(str(state.attributes.get(ATTR_FRIENDLY_NAME) or "").lower().split())
        if not name:
            continue
        entry = ent_reg.async_get(state.entity_id)
        if entry is None:
            continue
        thing_of[state.entity_id] = entry.device_id or state.entity_id
        area = entry.area_id
        if not area and entry.device_id and (device := dev_reg.async_get(entry.device_id)):
            area = device.area_id
        for assistant in assistants:
            if (entry.options.get(assistant) or {}).get("should_expose") is True:
                by_name[(assistant, name)].append((state.entity_id, area))
    clashes: dict[str, set[str]] = {}
    for (assistant, name), found in by_name.items():
        if len(found) < 2:
            continue
        if assistant == "conversation":
            areas = [a for _, a in found]
            same = {e for e, a in found if a is None or areas.count(a) > 1}
            if len(same) < 2:
                continue
            found = [(e, a) for e, a in found if e in same]
        if len({thing_of[e] for e, _ in found}) < 2:
            continue
        clashes.setdefault(name, set()).update(e for e, _ in found)
    items = []
    for name, entities in sorted(clashes.items()):
        key = f"voice:{name}"
        if key in keep:
            continue
        ids = sorted(entities)
        shown = str(hass.states.get(ids[0]).attributes.get(ATTR_FRIENDLY_NAME))
        items.append(Item(key=key, name=shown, id=ids[0], info=", ".join(ids), link="/config/entities", hint="samename",
                          used_by=ids[:4], used_n=len(ids)))
    if not items:
        return []
    return [
        Finding(
            kind="voice_names",
            title=f"{_plural(len(items), 'name is', 'names are')} used twice for voice",
            detail="A voice assistant cannot tell them apart.",
            severity="info",
            link="/config/voice-assistants/expose",
            items=items,
        )
    ]


# ---- 16. Before you update -----------------------------------------------------------------------------------


@callback
def check_before_update(
    hass: HomeAssistant, findings: list[Finding], backup: dict[str, Any] | None, now: float | None = None,
    keep: frozenset[str] = frozenset(),
) -> list[Finding]:
    """One calm answer when updates are waiting: is the backup fresh, has the storage room, do the notes warn?"""
    now = now if now is not None else time.time()
    waiting = [s for s in hass.states.async_all("update") if s.state == "on"]
    if not waiting:
        return []
    items: list[Item] = []
    last = (backup or {}).get("last")
    if backup is not None:
        fresh = last is not None and now - last <= BACKUP_FRESH.total_seconds()
        items.append(Item(key="before:backup", name="Backup", id="backup", link="/config/backup", good=fresh,
                          hint="upd_backup_ok" if fresh else "upd_backup",
                          info="Fresh" if fresh else "Make one first",
                          since=dt_util.utc_from_timestamp(last).isoformat() if last else ""))
    storage = next((f for f in findings if f.kind == "storage" and f.severity == "warning"), None)
    items.append(Item(key="before:storage", name="Storage", id="storage", link="/config/storage", good=storage is None,
                      hint="upd_storage_ok" if storage is None else "upd_storage",
                      info="Has room" if storage is None else "Free some space first"))
    risky = next((f for f in findings if f.kind == "updates"), None)
    names = [i.name for i in risky.items] if risky else []
    items.append(Item(key="before:notes", name="Release notes", id="notes", link="/config/updates", good=not names,
                      hint="upd_notes_ok" if not names else "upd_notes",
                      info="No breaking change found" if not names else f"Read first: {', '.join(names[:3])}",
                      used_by=names[:3], used_n=len(names)))
    items = [i for i in items if i.key not in keep]
    if not items:
        return []
    return [
        Finding(
            kind="before_update",
            title=f"{_plural(len(waiting), 'update is', 'updates are')} waiting",
            detail="Safe to update when all three are fine.",
            severity="info",
            link="/config/updates",
            items=items,
        )
    ]


@callback
def ignored_by_label(hass: HomeAssistant) -> tuple[set[str], set[str], int]:
    """What carries the label "checkup_ignore": entity ids, device ids, and how many labels were set by hand.

    A label on a device covers its entities. A label on an area covers its devices and entities.
    """
    try:
        if lr.async_get(hass).async_get_label(IGNORE_LABEL) is None:
            return set(), set(), 0
    except Exception:  # noqa: BLE001 - no labels on this Home Assistant
        return set(), set(), 0
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    areas = {a.id for a in ar.async_get(hass).async_list_areas() if IGNORE_LABEL in a.labels}
    devices = {d.id for d in dev_reg.devices.values() if IGNORE_LABEL in d.labels}
    by_hand = len(areas) + len(devices)
    devices |= {d.id for d in dev_reg.devices.values() if d.area_id in areas}
    entities: set[str] = set()
    for entry in ent_reg.entities.values():
        if IGNORE_LABEL in entry.labels:
            by_hand += 1
            entities.add(entry.entity_id)
        elif entry.device_id in devices or (entry.area_id in areas):
            entities.add(entry.entity_id)
    return entities, devices, by_hand


def run_checks(
    hass: HomeAssistant,
    watch: LogWatch,
    corpus: set[str] | None,
    started_at: datetime | None,
    keep: set[str],
    now: float | None = None,
    watching_since: float = 0.0,
    run_start: float = 0.0,
    facts: YamlFacts | None = None,
    offline: dict[str, list[Any]] | None = None,
    drops: dict[str, list[float]] | None = None,
    update_notes: dict[str, list[str]] | None = None,
    backup: dict[str, Any] | None = None,
    storage: dict[str, float] | None = None,
    storage_samples: list[list[float]] | None = None,
    changes: ChangeCounter | None = None,
    weak: dict[str, float] | None = None,
) -> list[Finding]:
    # The label "checkup_ignore" works like "Ignore" on the page, for a whole device or area at once.
    try:
        no_entities, no_devices, _ = ignored_by_label(hass)
    except Exception:  # noqa: BLE001
        no_entities, no_devices = set(), set()
    kept = frozenset(keep) | frozenset(
        f"{kind}:{entity_id}" for entity_id in no_entities for kind in ("unavailable", "entity", "battery", "helper", "idle", "chatty", "signal")
    ) | frozenset(
        f"{kind}:{device_id}" for device_id in no_devices for kind in ("offline_device", "offline_parts", "device", "area", "signal")
    )
    hidden = no_entities | no_devices
    findings: list[Finding] = []
    for number, check in enumerate((
        lambda: check_failed_integrations(hass, kept),
        lambda: check_log(hass, watch, now or time.time(), kept, watching_since, run_start, drops),
        lambda: check_broken_references(hass, kept, facts),
        lambda: check_leftovers(hass, kept, started_at),
        lambda: check_unavailable(hass, started_at, kept, offline),
        lambda: check_unused_helpers(hass, corpus, kept),
        lambda: check_batteries(hass, kept),
        lambda: check_updates(hass, kept, update_notes),
        lambda: check_areas(hass, kept),
        lambda: check_idle_automations(hass, kept),
        lambda: check_backup(hass, kept, backup),
        lambda: check_storage(kept, storage, storage_samples, now),
        lambda: check_history(hass, kept, changes, now),
        lambda: check_signal(hass, kept, weak, now),
        lambda: check_voice_names(hass, kept),
    )):
        try:
            findings.extend(check())
        except Exception:  # noqa: BLE001 - one broken check must not hide the others
            # Said out loud (once per check): a check that fails must not look like "all fine".
            if number not in _FAILED_ONCE:
                _FAILED_ONCE.add(number)
                _LOGGER.warning("A Home Checkup check could not run. Please report it.", exc_info=True)
            else:
                _LOGGER.debug("A Home Checkup check failed", exc_info=True)
    try:
        # Last, because it reads the other answers.
        findings.extend(check_before_update(hass, findings, backup, now, kept))
    except Exception:  # noqa: BLE001
        _LOGGER.debug("The before-update check failed", exc_info=True)
    if hidden:
        # The lists that are not keyed by the thing itself (waiting updates, broken steps of an automation).
        for finding in findings:
            if finding.kind in ("updates", "broken_references"):
                finding.items = [i for i in finding.items if i.id not in hidden]
        findings = [f for f in findings if f.items]
    return findings
