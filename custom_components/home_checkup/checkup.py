"""Runs the checks on a schedule and keeps the latest report.

1. Live: a log handler counts warnings and errors by cause (cheap, in memory).
2. Every hour: the registries and the log counts are checked again (cheap, no file reads).
3. Once a day (8:00) and a few minutes after start: also reads the YAML files to see which helpers are used.
The tablets only read one small sensor; the full report is sent only when someone opens it.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, EVENT_STATE_CHANGED
from homeassistant.core import CoreState, Event, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later, async_track_time_change, async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.loader import async_get_loaded_integration
from homeassistant.util import dt as dt_util

from .checks import (
    Finding,
    Item,
    YamlFacts,
    broken_refs,
    integration_name,
    read_corpus,
    read_update_notes,
    ChangeCounter,
    read_backup,
    read_storage,
    note_storage,
    read_yaml_facts,
    run_checks,
    ignored_by_label,
)
from .checks import checked_counts
from .fixes import Fixes
from .const import (
    CHECK_GROUPS,
    CONF_AUTO_RESTART,
    CONF_AUTO_UPDATE,
    CONF_CHECKS_OFF,
    CONF_DAILY_HOUR,
    CONF_REPAIRS_NOTE,
    CONF_WEEKLY_LETTER,
    UPDATE_HOUR,
)
from .const import DAILY_HOUR, DOMAIN, FIRST_SCAN_DELAY, LETTER_MIN_GAP, LETTER_NAMES, LETTER_SHOWN, LETTER_WEEKDAY, NEW_FOR, REFRESH_EVERY, STARTUP_GRACE, STOPPED_AFTER, STOPPED_SHOWN
from .logwatch import LogWatch
from .repairs import async_mark_covered, async_sync_issues

_LOGGER = logging.getLogger(__name__)
STORE_VERSION = 1


_LETTER_WORDS = {
    "en": ("Home Checkup: your week", "Gone this week: {names}.", "New this week: {names}.", "and {n} more",
           "1 other thing still waits.", "{n} other things still wait.", "Nothing else waits."),
    "fr": ("Home Checkup : votre semaine", "Réglé cette semaine : {names}.", "Nouveau cette semaine : {names}.", "et {n} de plus",
           "1 autre point attend encore.", "{n} autres points attendent encore.", "Rien d’autre n’attend."),
    "de": ("Home Checkup: Ihre Woche", "Diese Woche erledigt: {names}.", "Neu in dieser Woche: {names}.", "und {n} weitere",
           "1 weiterer Punkt wartet noch.", "{n} weitere Punkte warten noch.", "Sonst wartet nichts."),
    "es": ("Home Checkup: tu semana", "Resuelto esta semana: {names}.", "Nuevo esta semana: {names}.", "y {n} más",
           "1 cosa más sigue esperando.", "{n} cosas más siguen esperando.", "No espera nada más."),
}


def letter_text(letter: dict[str, Any], language: str = "en") -> tuple[str, str]:
    """The weekly letter as a title and a few short lines. Names, not numbers."""
    title, gone, new, more, one, many, none = _LETTER_WORDS.get((language or "en")[:2], _LETTER_WORDS["en"])

    def names(key: str) -> str:
        shown = letter.get(key, [])
        extra = letter.get(f"{key}_n", len(shown)) - len(shown)
        return ", ".join(shown) + (f" {more.format(n=extra)}" if extra > 0 else "")

    lines = []
    if letter.get("gone"):
        lines.append(gone.format(names=names("gone")))
    if letter.get("new"):
        lines.append(new.format(names=names("new")))
    still = letter.get("still", 0)
    lines.append(none if still <= 0 else one if still == 1 else many.format(n=still))
    return title, "\n".join(lines)


@callback
def letter_places(hass: HomeAssistant) -> dict[str, str]:
    """Where the weekly letter can go: a Home Assistant notification, or a phone that exists here."""
    places = {"off": "Off", "persistent": "Home Assistant notification"}
    # Only phones and tablets with the Home Assistant app: a short list with readable names. A letter is read, not spoken.
    for name in sorted(hass.services.async_services().get("notify", {})):
        if name.startswith("mobile_app_"):
            places[name] = name.removeprefix("mobile_app_").replace("_", " ").title()
    return places


@callback
def own_update(hass: HomeAssistant) -> str | None:
    """The update entity of Home Checkup itself (made by HACS), or None."""
    for state in hass.states.async_all("update"):
        names = f"{state.attributes.get('title') or ''} {state.attributes.get('friendly_name') or ''}".lower()
        if "home checkup" in names:
            return state.entity_id
    return None


def _version_on_disk() -> str:
    try:
        return str(json.loads((Path(__file__).parent / "manifest.json").read_text(encoding="utf-8")).get("version") or "")
    except Exception:  # noqa: BLE001
        return ""


def _code_print() -> str:
    """A fingerprint of everything that needs a restart to change: the Python files and what the manifest asks for.

    The page file, the words and the version number are left out: a new copy of those works with no restart."""
    here = Path(__file__).parent
    digest = hashlib.sha256()
    try:
        for file in sorted(here.glob("*.py")):
            digest.update(file.name.encode())
            digest.update(file.read_bytes())
        manifest = json.loads((here / "manifest.json").read_text(encoding="utf-8"))
        manifest.pop("version", None)
        digest.update(json.dumps(manifest, sort_keys=True).encode())
    except Exception:  # noqa: BLE001
        return ""
    return digest.hexdigest()


def _counted(finding: Finding) -> bool:
    return finding.severity == "warning" and finding.in_note


class Checkup:
    def __init__(self, hass: HomeAssistant, started_at: datetime | None) -> None:
        self.hass = hass
        self.started_at = started_at
        self.watch = LogWatch()
        self.keep: set[str] = set()
        self.findings: list[Finding] = []
        self.scanned_at: datetime | None = None
        self.corpus: set[str] | None = None
        self.yaml_facts: YamlFacts | None = None
        self.update_notes: dict[str, list[str]] = {}  # update entity -> [version, release notes], in memory only
        self.repairs_note = True
        self.fixes = Fixes(hass)
        # When each item was first and last seen, to mark what is new since yesterday.
        self._seen: dict[str, list[float]] = {}
        self._seen_since: float = 0.0
        self._offline: dict[str, list[Any]] = {}  # entity id -> [offline since, exact]; outlives restarts
        self._drops: dict[str, list[float]] = {}  # log item key -> when it came back, this week
        self.backup: dict[str, Any] | None = None  # when the newest backup was made; read with the full check
        self.storage: dict[str, float] | None = None  # sizes only; read with the full check
        self._disk: list[list[float]] = []  # [when, used bytes], one per half day; outlives restarts
        self._weak: dict[str, float] = {}  # entity id -> weak signal since; outlives restarts
        self.changes = ChangeCounter()  # how often each entity changes; in memory only, only counts
        # The weekly letter: what was open at the last letter (key -> name), and the last letter itself.
        self.checks_off: set[str] = set()  # checks the person turned off behind the gear
        self.daily_hour = DAILY_HOUR
        self.auto_update = False
        self.auto_restart = False
        self.restart_wanted = ""  # a newer version is on the disk and its code changed: it starts after a restart
        self._page_only = ""  # a newer version is on the disk and only its page changed: it already runs
        self._unsub_daily: Callable[[], None] | None = None
        self.weekly_letter = "off"  # where the letter is sent: "off", "persistent", or a notify service name
        self._week: dict[str, Any] = {}
        self.letter: dict[str, Any] | None = None
        self._seen_store: Store[dict[str, Any]] = Store(hass, STORE_VERSION, f"{DOMAIN}.seen")
        self._store: Store[dict[str, Any]] = Store(hass, STORE_VERSION, f"{DOMAIN}.keep")
        # The error history (counts and redacted samples only), so it survives a restart.
        self._log_store: Store[dict[str, Any]] = Store(hass, STORE_VERSION, f"{DOMAIN}.log")
        self.watching_since: float = 0.0
        # When this run of Home Assistant began. Start-up errors from before it belong to an earlier start.
        # After a reload the start is a guess, so some minutes are allowed before it.
        self.run_start: float = started_at.timestamp() - 3 * STARTUP_GRACE if started_at else 0.0
        # "Did it work?": the log next steps someone took, by integration ("" is Home Assistant itself).
        self._acted: dict[str, dict[str, Any]] = {}
        self._listeners: list[Callable[[], None]] = []
        self._unsubs: list[Callable[[], None]] = []
        self._unsub_started: Callable[[], None] | None = None

    # ---- life cycle -----------------------------------------------------------------------------------------

    async def async_start(self) -> None:
        data = await self._store.async_load() or {}
        self.keep = set(data.get("keep", []))
        await self.fixes.async_load()
        seen = await self._seen_store.async_load() or {}
        self._seen = seen.get("seen", {})
        self._seen_since = seen.get("since") or time.time()
        self._offline = seen.get("offline", {})
        self._drops = seen.get("drops", {})
        self._disk = seen.get("disk", [])
        self._weak = seen.get("weak", {})
        self._week = seen.get("week", {})
        self.letter = seen.get("letter")
        self._unsubs.append(self.hass.bus.async_listen(EVENT_STATE_CHANGED, self._count_change))
        log = await self._log_store.async_load() or {}
        self.watching_since = float(log.get("since") or time.time())
        self._acted = log.get("acted", {})
        self.watch.load(log.get("groups", []))
        if self.started_at is None:
            # Home Assistant is starting now. The history was last saved when the run before this one ended, so
            # everything after that moment belongs to this start (also the errors from before we were loaded).
            self.run_start = float(log.get("saved_at") or 0) or time.time() - STARTUP_GRACE
        if self.started_at is not None:  # Home Assistant was already running (a reload or a new install)
            self.watch.startup_until = self.started_at.timestamp() + STARTUP_GRACE
        logging.getLogger().addHandler(self.watch)
        self.watch.take_system_log(self.hass, after=float(log.get("saved_at") or 0))
        self._unsubs.append(async_track_time_interval(self.hass, self._hourly, REFRESH_EVERY))
        self._track_daily()
        # The code as it was loaded. Taken once per run of Home Assistant, so a reload cannot mistake new files for it.
        if f"{DOMAIN}_code" not in self.hass.data:
            self.hass.data[f"{DOMAIN}_code"] = await self.hass.async_add_executor_job(_code_print)
        self._unsubs.append(async_track_time_change(self.hass, self._nightly, hour=UPDATE_HOUR, minute=0, second=0))
        if self.hass.state is CoreState.running:
            self._unsubs.append(async_call_later(self.hass, FIRST_SCAN_DELAY, self._daily))
        else:
            self._unsub_started = self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, self._on_started)
        self.refresh()

    @callback
    def _track_daily(self) -> None:
        if self._unsub_daily:
            self._unsub_daily()
        self._unsub_daily = async_track_time_change(self.hass, self._daily, hour=self.daily_hour, minute=0, second=0)

    @callback
    def apply_settings(self, options: dict[str, Any], started: bool = True) -> None:
        """The settings behind the gear. A change applies at once, with no reload."""
        self.repairs_note = options.get(CONF_REPAIRS_NOTE, True)
        self.weekly_letter = options.get(CONF_WEEKLY_LETTER, "off")
        self.checks_off = {name for name in options.get(CONF_CHECKS_OFF, []) if name in CHECK_GROUPS}
        self.auto_update = bool(options.get(CONF_AUTO_UPDATE, False))
        self.auto_restart = self.auto_update and bool(options.get(CONF_AUTO_RESTART, False))
        hour = int(options.get(CONF_DAILY_HOUR, DAILY_HOUR))
        if hour != self.daily_hour:
            self.daily_hour = hour
            if started:
                self._track_daily()
        if started:
            self.refresh()

    def settings(self) -> dict[str, Any]:
        return {
            CONF_REPAIRS_NOTE: self.repairs_note,
            CONF_WEEKLY_LETTER: self.weekly_letter,
            "places": [[key, label] for key, label in letter_places(self.hass).items()],
            CONF_CHECKS_OFF: sorted(self.checks_off),
            "checks": list(CHECK_GROUPS),
            CONF_DAILY_HOUR: self.daily_hour,
            CONF_AUTO_UPDATE: self.auto_update,
            CONF_AUTO_RESTART: self.auto_restart,
            "can_update": own_update(self.hass) is not None,
        }

    async def _nightly(self, _now: Any = None) -> None:
        await self.async_auto_update()

    async def async_auto_update(self) -> str:
        """At night, only when the person turned it on: install a waiting version of Home Checkup itself.

        Returns what happened: "off", "none", "failed", "installed" or "restarting"."""
        if not self.auto_update:
            return "off"
        entity_id = own_update(self.hass)
        state = self.hass.states.get(entity_id) if entity_id else None
        if state is None or state.state != "on" or state.attributes.get("in_progress"):
            return "none"
        try:
            await self.hass.services.async_call("update", "install", {"entity_id": entity_id}, blocking=True)
        except Exception:  # noqa: BLE001 - HACS could not install it: nothing changed, HACS shows why
            _LOGGER.debug("Could not install the update", exc_info=True)
            return "failed"
        await self._read_disk_version()
        if not self.restart_wanted:
            return "failed"
        self.refresh()
        if not self.auto_restart:
            return "installed"
        await self.hass.services.async_call("homeassistant", "restart", {})
        return "restarting"

    async def _read_disk_version(self) -> None:
        from .panel import async_refresh_panel  # noqa: PLC0415

        on_disk = await self.hass.async_add_executor_job(_version_on_disk)
        loaded = self._loaded_version
        self.restart_wanted = self._page_only = ""
        if on_disk and loaded and on_disk != loaded:
            code = await self.hass.async_add_executor_job(_code_print)
            if code and code == self.hass.data.get(f"{DOMAIN}_code"):
                self._page_only = on_disk  # only the page changed: it works at once
            else:
                self.restart_wanted = on_disk
        try:
            await async_refresh_panel(self.hass)
        except Exception:  # noqa: BLE001
            _LOGGER.debug("Could not point the sidebar at the new page", exc_info=True)

    async def async_restart(self) -> bool:
        """The Restart button on the page. Only offered, and only allowed, while a new version waits for it."""
        if not self.restart_wanted:
            return False
        await self.hass.services.async_call("homeassistant", "restart", {})
        return True

    @callback
    def _count_change(self, event: Event) -> None:
        self.changes.add(event.data["entity_id"])

    @callback
    def async_stop(self) -> None:
        logging.getLogger().removeHandler(self.watch)
        if self._unsub_started is not None:
            self._unsub_started()
            self._unsub_started = None
        if self._unsub_daily:
            self._unsub_daily()
            self._unsub_daily = None
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()

    @callback
    def _on_started(self, _event: Event) -> None:
        self._unsub_started = None  # fired; removing it again would log an error
        self.started_at = dt_util.utcnow()
        self.watch.startup_until = time.time() + STARTUP_GRACE
        self._unsubs.append(async_call_later(self.hass, FIRST_SCAN_DELAY, self._daily))

    # ---- scans ------------------------------------------------------------------------------------------------

    @callback
    def _hourly(self, _now: Any = None) -> None:
        self.refresh()

    async def _daily(self, _now: Any = None) -> None:
        await self.async_full_scan()
        await self.async_weekly()

    def _open_now(self) -> dict[str, str]:
        """What needs a look right now: key -> name. Only what is counted; notes and things to watch stay out."""
        return {i.key: i.name for f in self.findings if _counted(f) for i in f.items}

    async def async_weekly(self, now: float | None = None, force: bool = False) -> dict[str, Any] | None:
        """The weekly letter, on Sunday morning: what went away, what is new. No letter in a week with no change.

        It is always kept for the page. It is sent to a phone only when the person chose where."""
        now = now if now is not None else time.time()
        if self.letter and now - self.letter.get("at", 0) > LETTER_SHOWN.total_seconds():
            self.letter = None
        open_now = self._open_now()
        if not self._week:
            self._week = {"start": now, "keys": open_now}
            self._save_seen()
            return None
        due = dt_util.as_local(dt_util.utc_from_timestamp(now)).weekday() == LETTER_WEEKDAY
        if not force and (not due or now - self._week.get("start", 0) < LETTER_MIN_GAP.total_seconds()):
            return None
        before: dict[str, str] = self._week.get("keys", {})
        gone = sorted(name for key, name in before.items() if key not in open_now and key not in self.keep)
        new = sorted(name for key, name in open_now.items() if key not in before)
        self._week = {"start": now, "keys": open_now}
        letter = None
        if gone or new:
            letter = {
                "at": now,
                "gone": gone[:LETTER_NAMES], "gone_n": len(gone),
                "new": new[:LETTER_NAMES], "new_n": len(new),
                "still": len(open_now) - len(new),
            }
            self.letter = letter
            await self._send_letter(letter)
        self._save_seen()
        for listener in list(self._listeners):
            listener()
        return letter

    async def _send_letter(self, letter: dict[str, Any]) -> None:
        if self.weekly_letter in ("", "off"):
            return
        title, message = letter_text(letter, self.hass.config.language)
        try:
            if self.weekly_letter == "persistent":
                await self.hass.services.async_call(
                    "persistent_notification", "create",
                    {"title": title, "message": message, "notification_id": f"{DOMAIN}_letter"},
                )
            elif self.hass.services.has_service("notify", self.weekly_letter):
                await self.hass.services.async_call("notify", self.weekly_letter, {"title": title, "message": message})
        except Exception:  # noqa: BLE001 - a letter that cannot be sent is still on the page
            _LOGGER.debug("Could not send the weekly letter", exc_info=True)

    def _page(self) -> str:
        from .panel import page_version  # noqa: PLC0415

        return page_version(self.hass)

    def _seen_data(self) -> dict[str, Any]:
        return {
            "seen": self._seen, "since": self._seen_since, "offline": self._offline, "drops": self._drops,
            "disk": self._disk, "weak": self._weak, "week": self._week, "letter": self.letter,
        }

    def _save_seen(self) -> None:
        self._seen_store.async_delay_save(self._seen_data, 60)

    async def async_full_scan(self) -> None:
        """Read the configuration files (in a worker thread), then check everything."""
        try:
            self.corpus = await self.hass.async_add_executor_job(read_corpus, self.hass.config.config_dir)
        except Exception:  # noqa: BLE001 - without the files, the helper check is simply skipped
            _LOGGER.debug("Could not read the configuration files", exc_info=True)
            self.corpus = None
        try:
            self.yaml_facts = await self.hass.async_add_executor_job(
                read_yaml_facts, self.hass.config.config_dir, broken_refs(self.hass)
            )
        except Exception:  # noqa: BLE001 - without the files, the buttons are offered as before
            _LOGGER.debug("Could not read where automations and scripts are written", exc_info=True)
            self.yaml_facts = None
        try:
            self.update_notes = await read_update_notes(self.hass, self.update_notes)
        except Exception:  # noqa: BLE001 - without the notes, only the version step is judged
            _LOGGER.debug("Could not read release notes", exc_info=True)
        try:
            self.backup = await read_backup(self.hass)
        except Exception:  # noqa: BLE001 - without the list, nothing is said about backups
            _LOGGER.debug("Could not read the backup list", exc_info=True)
            self.backup = None
        try:
            self.storage = await self.hass.async_add_executor_job(read_storage, self.hass.config.config_dir)
            note_storage(self._disk, self.storage, time.time())
        except Exception:  # noqa: BLE001
            _LOGGER.debug("Could not read the storage", exc_info=True)
            self.storage = None
        try:
            await self._read_disk_version()
        except Exception:  # noqa: BLE001
            self.restart_wanted = ""
        self.refresh()

    @callback
    def refresh(self) -> None:
        now = time.time()
        self.changes.turn(now)
        self.findings = run_checks(
            self.hass, self.watch, self.corpus, self.started_at, self.keep, now,
            watching_since=self.watching_since, run_start=self.run_start, facts=self.yaml_facts, offline=self._offline, drops=self._drops, update_notes=self.update_notes,
            backup=self.backup, storage=self.storage, storage_samples=self._disk,
            changes=self.changes, weak=self._weak,
        )
        self.findings += self._stopped(now)
        if self.checks_off:
            off = {kind for name in self.checks_off for kind in CHECK_GROUPS.get(name, ())}
            self.findings = [f for f in self.findings if f.kind not in off]
        self._mark_new(now)
        async_mark_covered(self.hass, self.findings)
        self._log_store.async_delay_save(self._log_data, 60)
        self.scanned_at = dt_util.utcnow()
        async_sync_issues(self.hass, self.findings if self.repairs_note else [])
        for listener in list(self._listeners):
            listener()

    @callback
    def _mark_new(self, now: float) -> None:
        """Mark items first seen in the last 24 hours. Nothing is "new" on the very first checkup."""
        baseline_until = self._seen_since + 1800
        for finding in self.findings:
            for item in finding.items:
                first, _last = self._seen.get(item.key, (now, now))
                self._seen[item.key] = [first, now]
                item.new = first > baseline_until and now - first < NEW_FOR.total_seconds()
        week = 7 * 86400
        self._seen = {k: v for k, v in self._seen.items() if now - v[1] < week}
        self._save_seen()

    def _log_data(self) -> dict[str, Any]:
        return {
            "since": self.watching_since,
            "saved_at": time.time(),
            "groups": self.watch.saved(),
            "acted": self._acted,
        }

    # ---- did it work? -------------------------------------------------------------------------------------------

    async def async_acted(self, integration: str, action: str) -> None:
        """Someone took the next step for an integration's errors. Home Checkup looks again later."""
        self._acted[integration] = {"at": time.time(), "action": action}
        self._log_store.async_delay_save(self._log_data, 5)

    @callback
    def _stopped(self, now: float) -> list[Finding]:
        """Errors that stopped after someone took the next step. Shown as good news for a few days."""
        out: list[Finding] = []
        last_error: dict[str, float] = {}
        for group, _count in self.watch.groups(now):
            if group.level in ("ERROR", "CRITICAL"):
                key = group.domain or ""
                last_error[key] = max(last_error.get(key, 0.0), group.last_seen)
        for integration, acted in list(self._acted.items()):
            at = float(acted.get("at", 0))
            if last_error.get(integration, 0.0) > at + 600:  # still happening: no good news; forget it after a day
                if now - at > 86400:
                    del self._acted[integration]
                continue
            if now - at < STOPPED_AFTER.total_seconds():
                continue
            if now - at > STOPPED_SHOWN.total_seconds():
                del self._acted[integration]
                continue
            key = f"stopped:{integration}"
            if key in self.keep:
                continue
            name = integration_name(self.hass, integration or None)
            out.append(
                Finding(
                    kind="log_stopped",
                    title=f"{name}: the errors stopped",
                    detail="No errors since you took the next step.",
                    severity="info",
                    integration=integration or None,
                    integration_name=name,
                    in_note=False,
                    action=str(acted.get("action", "")),
                    items=[Item(key=key, name=name, id=integration or "homeassistant")],
                )
            )
        return out

    # ---- keep list --------------------------------------------------------------------------------------------

    async def async_set_keep(self, key: str | list[str], keep: bool) -> None:
        keys = [key] if isinstance(key, str) else key
        if keep:
            self.keep.update(keys)
        else:
            self.keep.difference_update(keys)
        await self._store.async_save({"keep": sorted(self.keep)})
        self.refresh()

    # ---- what others read ---------------------------------------------------------------------------------------

    @callback
    def add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)

    @property
    def version(self) -> str:
        """This version of Home Checkup, for the page ("Ask for a fix" names it)."""
        return self._page_only or self._loaded_version

    @property
    def _loaded_version(self) -> str:
        try:
            return str(async_get_loaded_integration(self.hass, DOMAIN).version or "")
        except Exception:  # noqa: BLE001 - not loaded through the loader (some tests)
            return ""

    @property
    def count(self) -> int:
        """Things that need a look: one number for the page, the sensor, the Studio card and the Repairs note.

        Not counted: notes marked "info", and things "to watch" (a short burst of log errors, or a problem that
        already has Home Assistant's own repair note)."""
        return sum(1 for f in self.findings if _counted(f))

    @property
    def watch_count(self) -> int:
        """Things to watch: shown under their own heading, not counted."""
        return sum(1 for f in self.findings if f.severity == "warning" and not f.in_note)

    @property
    def headline(self) -> str:
        n = self.count
        if n == 0:
            return "Home is healthy"
        return "1 thing needs a look" if n == 1 else f"{n} things need a look"

    def summary(self) -> list[str]:
        """The daily summary as short sentences, most important first."""
        lines = [f.title + "." for f in self.findings if _counted(f)]
        lines += [f.title + "." for f in self.findings if not _counted(f)]
        return lines or ["Nothing needs a look today."]

    async def async_reload_entry(self, key: str) -> bool:
        """Home Assistant's own Reload for an integration that did not start. True when it runs afterwards."""
        from homeassistant.config_entries import ConfigEntryState  # noqa: PLC0415

        entry = self.hass.config_entries.async_get_entry(key.removeprefix("entry:"))
        if entry is None or not any(i.key == key and i.fix == "reload" for f in self.findings for i in f.items):
            return False
        try:
            await self.hass.config_entries.async_reload(entry.entry_id)
        except Exception:  # noqa: BLE001 - a reload that is not allowed right now changes nothing
            _LOGGER.debug("Could not reload %s", entry.domain, exc_info=True)
        return entry.state is ConfigEntryState.LOADED

    def report(self) -> dict[str, Any]:
        findings = sorted(self.findings, key=lambda f: 0 if _counted(f) else 1 if f.severity == "warning" else 2)
        return {
            "status": "healthy" if self.count == 0 else "attention",
            "count": self.count,
            "watch": self.watch_count,
            "version": self.version,
            "headline": self.headline,
            "summary": self.summary(),
            "scanned_at": self.scanned_at.isoformat() if self.scanned_at else None,
            "helpers_checked": self.corpus is not None,
            "checked": checked_counts(self.hass),
            "findings": [f.as_dict() for f in findings],
            "kept": sorted(self.keep),
            "labelled": ignored_by_label(self.hass)[2],
            "letter": self.letter,
            "off": sorted(self.checks_off),
            "restart": self.restart_wanted,
            "page": self._page(),
        }
