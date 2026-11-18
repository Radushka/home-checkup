"""Runs the checks on a schedule and keeps the latest report.

1. Live: a log handler counts warnings and errors by cause (cheap, in memory).
2. Every hour: the registries and the log counts are checked again (cheap, no file reads).
3. Once a day (8:00) and a few minutes after start: also reads the YAML files to see which helpers are used.
The tablets only read one small sensor; the full report is sent only when someone opens it.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, Event, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later, async_track_time_change, async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.loader import async_get_loaded_integration
from homeassistant.util import dt as dt_util

from .checks import Finding, Item, integration_name, read_corpus, run_checks
from .fixes import Fixes
from .const import DAILY_HOUR, DOMAIN, FIRST_SCAN_DELAY, NEW_FOR, REFRESH_EVERY, STARTUP_GRACE, STOPPED_AFTER, STOPPED_SHOWN
from .logwatch import LogWatch
from .repairs import async_mark_covered, async_sync_issues

_LOGGER = logging.getLogger(__name__)
STORE_VERSION = 1


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
        self.repairs_note = True
        self.fixes = Fixes(hass)
        # When each item was first and last seen, to mark what is new since yesterday.
        self._seen: dict[str, list[float]] = {}
        self._seen_since: float = 0.0
        self._seen_store: Store[dict[str, Any]] = Store(hass, STORE_VERSION, f"{DOMAIN}.seen")
        self._store: Store[dict[str, Any]] = Store(hass, STORE_VERSION, f"{DOMAIN}.keep")
        # The error history (counts and redacted samples only), so it survives a restart.
        self._log_store: Store[dict[str, Any]] = Store(hass, STORE_VERSION, f"{DOMAIN}.log")
        self.watching_since: float = 0.0
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
        log = await self._log_store.async_load() or {}
        self.watching_since = float(log.get("since") or time.time())
        self._acted = log.get("acted", {})
        self.watch.load(log.get("groups", []))
        if self.started_at is not None:  # Home Assistant was already running (a reload or a new install)
            self.watch.startup_until = self.started_at.timestamp() + STARTUP_GRACE
        logging.getLogger().addHandler(self.watch)
        self.watch.take_system_log(self.hass, after=float(log.get("saved_at") or 0))
        self._unsubs.append(async_track_time_interval(self.hass, self._hourly, REFRESH_EVERY))
        self._unsubs.append(async_track_time_change(self.hass, self._daily, hour=DAILY_HOUR, minute=0, second=0))
        if self.hass.state is CoreState.running:
            self._unsubs.append(async_call_later(self.hass, FIRST_SCAN_DELAY, self._daily))
        else:
            self._unsub_started = self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, self._on_started)
        self.refresh()

    @callback
    def async_stop(self) -> None:
        logging.getLogger().removeHandler(self.watch)
        if self._unsub_started is not None:
            self._unsub_started()
            self._unsub_started = None
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

    async def async_full_scan(self) -> None:
        """Read the configuration files (in a worker thread), then check everything."""
        try:
            self.corpus = await self.hass.async_add_executor_job(read_corpus, self.hass.config.config_dir)
        except Exception:  # noqa: BLE001 - without the files, the helper check is simply skipped
            _LOGGER.debug("Could not read the configuration files", exc_info=True)
            self.corpus = None
        self.refresh()

    @callback
    def refresh(self) -> None:
        now = time.time()
        self.findings = run_checks(
            self.hass, self.watch, self.corpus, self.started_at, self.keep, now, watching_since=self.watching_since
        )
        self.findings += self._stopped(now)
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
        self._seen_store.async_delay_save(lambda: {"seen": self._seen, "since": self._seen_since}, 60)

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

    async def async_set_keep(self, key: str, keep: bool) -> None:
        if keep:
            self.keep.add(key)
        else:
            self.keep.discard(key)
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
            "findings": [f.as_dict() for f in findings],
            "kept": sorted(self.keep),
        }
