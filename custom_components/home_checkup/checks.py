"""The checks. Every check only reads; nothing here changes the home.

Each check returns a list of Finding objects. A finding is one "thing to look at", with the items behind it.
Each item has a key, so a person can mark it "Keep" and it never shows again.
"""

from __future__ import annotations

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
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.loader import async_get_loaded_integration
from homeassistant.util import dt as dt_util

from .const import (
    BATTERY_LOW,
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
    UNAVAILABLE_AFTER,
    TEMPLATE_HELPER_DOMAINS,
    UNAVAILABLE_SINCE_START_AFTER,
)
from .logwatch import LogWatch
from .meanings import meaning_of

_LOGGER = logging.getLogger(__name__)

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
    # For broken automation steps: the one-tap fix Home Checkup can offer, and when the automation last ran.
    fix: str = ""  # "use_new" (a renamed entity), "remove_step" (only that step is broken) or "turn_off"
    old: str = ""  # the missing entity id
    to: str = ""  # use_new: the entity that looks like its new name
    to_name: str = ""
    choose: bool = False  # no new name was found: the person can choose another entity of the same kind
    gone: str = ""  # turn_off: the integration that was removed ("Roomba")
    gone_at: str = ""  # turn_off: when, ISO date
    last_ran: str = ""  # ISO time, "" when it never ran


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


# ---- 1. Log: warnings and errors grouped by integration and cause ---------------------------------------


@callback
def _clock(when: float) -> str:
    return dt_util.as_local(dt_util.utc_from_timestamp(when)).strftime("%H:%M")


def check_log(
    hass: HomeAssistant,
    watch: LogWatch,
    now: float | None = None,
    keep: frozenset[str] = frozenset(),
    watching_since: float = 0.0,
    run_start: float = 0.0,
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
        name = integration_name(hass, domain)
        for level_groups, is_error, word in ((errors, True, "error"), (warnings, False, "warning")):
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
            severity = "warning" if is_error and not startup else "info"
            if startup:
                detail = "Only right after a restart. Usually harmless, but it hides real errors."
            elif causes == 1:
                detail = "One cause, repeated."
            else:
                detail = f"{causes} different causes."
            hints = [meaning_of(f"{g.template} {g.sample}") for g, _ in level_groups]
            action, action_link, action_info = next_step(hass, domain, hints) if is_error else ("", "", "")
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
                    in_note=severity == "warning" and (len(hours) >= NOTE_HOURS or new),
                    link=f"/config/integrations/integration/{domain}" if domain else "/config/logs",
                    items=[
                        Item(
                            key=f"log:{domain}:{g.template}",
                            name=g.sample,
                            id=g.logger,
                            info=(
                                f"{_plural(n, 'time')}, only right after a restart, last at {_clock(g.last_seen)}"
                                if g.startup_only(since)
                                else f"{_plural(n, 'time')}, last at {_clock(g.last_seen)}"
                            ),
                            hint=meaning_of(f"{g.template} {g.sample}"),
                            startup=g.startup_only(since),
                        )
                        for g, n in level_groups
                    ],
                )
            )
    return findings


# ---- 2. Integrations that did not start ------------------------------------------------------------------


@callback
def check_failed_integrations(hass: HomeAssistant, keep: frozenset[str] = frozenset()) -> list[Finding]:
    items = [
        Item(
            key=f"entry:{entry.entry_id}",
            name=f"{integration_name(hass, entry.domain)}: {entry.title}",
            id=entry.entry_id,
            info=entry.reason or entry.state.value.replace("_", " "),
            link=f"/config/integrations/integration/{entry.domain}",
        )
        for entry in hass.config_entries.async_entries()
        if entry.state in FAILED_STATES and entry.disabled_by is None and entry.domain != DOMAIN
    ]
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


@callback
def check_unavailable(hass: HomeAssistant, started_at: datetime | None, keep: frozenset[str] = frozenset()) -> list[Finding]:
    now = dt_util.utcnow()
    ent_reg = er.async_get(hass)
    up_long = started_at is not None and now - started_at >= UNAVAILABLE_SINCE_START_AFTER
    items: list[Item] = []
    for state in hass.states.async_all():
        if state.state != STATE_UNAVAILABLE or state.attributes.get(ATTR_RESTORED):
            continue  # restored ones are leftovers or failed integrations, reported elsewhere
        since = state.last_changed
        long_time = now - since >= UNAVAILABLE_AFTER
        since_start = up_long and started_at is not None and since <= started_at + _START_SLACK
        if not (long_time or since_start):
            continue
        entry = ent_reg.async_get(state.entity_id)
        info = (
            f"Unavailable since {dt_util.as_local(since).strftime('%-d %b')}."
            if long_time
            else "Unavailable since Home Assistant last started."
        )
        items.append(
            Item(
                key=f"unavailable:{state.entity_id}",
                name=_entity_name(hass, entry, state.entity_id),
                id=state.entity_id,
                info=info,
                link="/config/entities",
            )
        )
    items = [i for i in items if i.key not in keep]
    if not items:
        return []
    return [
        Finding(
            kind="unavailable",
            title=f"{_plural(len(items), 'entity', 'entities')} unavailable for a long time",
            detail="The device may be off, unplugged or out of range. If it is gone for good, remove it.",
            link="/config/entities",
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
def check_broken_references(hass: HomeAssistant, keep: frozenset[str] = frozenset()) -> list[Finding]:
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
            can_fix = domain == "automation" and state is not None and bool(state.attributes.get("id"))
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
                        if not item.fix and (can_fix or domain == "script") and "." in target:
                            item.choose = True
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

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in CORPUS_SKIP_DIRS and not d.startswith(".")]
        for filename in filenames:
            lower = filename.lower()
            if lower.endswith((".yaml", ".yml")) and not any(part in lower for part in CORPUS_SKIP_NAME_PARTS):
                take(Path(dirpath) / filename)
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
            detail="Something outside Home Assistant (like Node-RED) may still use them. Mark those as Keep.",
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


# ---- All together ---------------------------------------------------------------------------------------------


def run_checks(
    hass: HomeAssistant,
    watch: LogWatch,
    corpus: set[str] | None,
    started_at: datetime | None,
    keep: set[str],
    now: float | None = None,
    watching_since: float = 0.0,
    run_start: float = 0.0,
) -> list[Finding]:
    kept = frozenset(keep)
    findings: list[Finding] = []
    for number, check in enumerate((
        lambda: check_failed_integrations(hass, kept),
        lambda: check_log(hass, watch, now or time.time(), kept, watching_since, run_start),
        lambda: check_broken_references(hass, kept),
        lambda: check_leftovers(hass, kept, started_at),
        lambda: check_unavailable(hass, started_at, kept),
        lambda: check_unused_helpers(hass, corpus, kept),
        lambda: check_batteries(hass, kept),
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
    return findings
