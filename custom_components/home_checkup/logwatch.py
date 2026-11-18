"""Groups Home Assistant's warnings and errors by cause, so 400 log lines become a few plain findings.

A small logging handler counts each message by its template (the text before the values are filled in),
in hourly buckets. Only the counts and the redacted sample are kept, for 7 days, in Home Assistant's own storage
folder, so errors that keep coming back are still seen after a restart. Nothing leaves the home.
Errors from before Home Checkup started are taken once from Home Assistant's own system log.
Before a message is kept, anything that looks like a password, key, token or email address is hidden.
"""

from __future__ import annotations

import logging
import re
import threading
import time
import traceback
from dataclasses import dataclass, field

from homeassistant.core import HomeAssistant

from .const import DOMAIN, LOG_DETAIL_LEN, LOG_HISTORY, LOG_MAX_GROUPS, LOG_SAMPLE_LEN, LOG_WINDOW

_PATH_DOMAIN = re.compile(r"[/\\](?:custom_components|homeassistant[/\\]components)[/\\]([a-z0-9_]+)[/\\]")
_NAME_DOMAIN = re.compile(r"^(?:homeassistant\.components|custom_components)\.([a-z0-9_]+)")
# Parts of Home Assistant that only pass a message on. When one of them logs an error, the real owner is
# the integration deeper in the traceback (an Eufy error raised inside a websocket command, for example).
_CARRIERS = frozenset({"websocket_api", "http", "api", "frontend", "config", "script", "automation", "homeassistant"})
_HOUR = 3600
_HIDDEN = "•••"
_REDACT = (
    # user:password@ in addresses, like rtsp://admin:1234@192.168.1.5
    (re.compile(r"(\b[a-z][a-z0-9+.-]*://)[^/\s:@]+:[^/\s@]+@", re.I), rf"\1{_HIDDEN}@"),
    # Bearer and Basic sign-ins
    (re.compile(r"\b(bearer|basic)\s+[A-Za-z0-9._~+/=-]+", re.I), rf"\1 {_HIDDEN}"),
    # key=value and "key": "value" for names that hold secrets
    (
        re.compile(
            r"""((?:api[_-]?key|apikey|access[_-]?token|refresh[_-]?token|auth[_-]?token|token|password|passwd|pwd|"""
            r"""pass|secret|client[_-]?secret|authorization|auth|session|cookie|sig|signature|key)["']?\s*[=:]\s*["']?)"""
            r"""[^\s"'&,;}\]]+""",
            re.I,
        ),
        rf"\1{_HIDDEN}",
    ),
    # web tokens (three dotted parts)
    (re.compile(r"\b[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"), _HIDDEN),
    # email addresses, also when cut short ("name@", "name@icloud") or partly starred ("na***@mail.com")
    (re.compile(r"(?<![\w.+*-])[\w.+*-]*\w[\w.+*-]*@(?:[\w-]+(?:\.[\w-]+)*)?"), _HIDDEN),
    # long random strings (keys, tokens)
    (re.compile(r"\b(?=[A-Za-z0-9_-]*\d)(?=[A-Za-z0-9_-]*[A-Za-z])[A-Za-z0-9_-]{32,}\b"), _HIDDEN),
)


def redact(text: str) -> str:
    """Hide passwords, keys, tokens and email addresses in a log message."""
    for pattern, replacement in _REDACT:
        text = pattern.sub(replacement, text)
    return text


def domain_of(logger_name: str, path: str | None = None, deeper: list[str] | None = None) -> str | None:
    """The integration that owns a log message, from its file path or its logger name.

    When the message comes from a part that only passes errors on (like the websocket API), the deepest other
    integration in the traceback is the owner. `deeper` is the list of file paths in the traceback, outer first.
    """
    found = None
    if path and (m := _PATH_DOMAIN.search(path)):
        found = m.group(1)
    elif m := _NAME_DOMAIN.match(logger_name or ""):
        found = m.group(1)
    if (found is None or found in _CARRIERS) and deeper:
        for frame_path in reversed(deeper):
            if (m := _PATH_DOMAIN.search(frame_path)) and m.group(1) not in _CARRIERS:
                return m.group(1)
    return found


def _traceback_paths(tb) -> list[str]:
    paths = []
    while tb is not None and len(paths) < 200:
        paths.append(tb.tb_frame.f_code.co_filename)
        tb = tb.tb_next
    return paths


_TB_FILE = re.compile(r'File "([^"]+)"')


@dataclass
class LogGroup:
    domain: str | None
    logger: str
    level: str
    template: str
    sample: str
    first_seen: float
    last_seen: float
    hours: dict[int, int] = field(default_factory=dict)
    late: dict[int, int] = field(default_factory=dict)  # the same, without start-up noise
    detail: str = ""  # the full text of the newest one, with its traceback (redacted like the sample)
    source: str = ""  # where it was logged: "components/tuya/light.py:120"
    cause: str = ""  # the real error behind a wrapper line: "TimeoutError: no reply from the station"

    def count(self, since: float) -> int:
        start = int(since // _HOUR)
        return sum(n for hour, n in self.hours.items() if hour >= start)

    def late_hours(self, since: float) -> int:
        """In how many different hours since `since` it happened outside start-up."""
        start = int(since // _HOUR)
        return sum(1 for hour, n in self.late.items() if n and hour >= start)

    def startup_only(self, since: float) -> bool:
        return self.count(since) > 0 and self.late_hours(since) == 0

    def as_saved(self) -> dict:
        return {
            "domain": self.domain,
            "logger": self.logger,
            "level": self.level,
            "template": self.template,
            "sample": self.sample,
            "first": self.first_seen,
            "last": self.last_seen,
            "hours": [[h, n] for h, n in self.hours.items()],
            "late": [[h, n] for h, n in self.late.items()],
            "detail": self.detail,
            "source": self.source,
            "cause": self.cause,
        }


class LogWatch(logging.Handler):
    """Counts warnings and errors by cause. Safe to call from any thread; each record costs a dict update."""

    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self._lock = threading.Lock()
        self._groups: dict[tuple, LogGroup] = {}
        # Until when errors count as start-up noise. None: Home Assistant is still starting, so all of them do.
        self.startup_until: float | None = None

    # logging.Handler
    def emit(self, record: logging.LogRecord) -> None:
        try:
            if record.name.startswith(f"custom_components.{DOMAIN}"):
                return
            template = record.msg if isinstance(record.msg, str) else type(record.msg).__name__
            if record.exc_info and record.exc_info[0] is not None:
                template = f"{template} [{record.exc_info[0].__name__}]"
            self.add(
                domain=domain_of(
                    record.name,
                    record.pathname,
                    _traceback_paths(record.exc_info[2]) if record.exc_info and record.exc_info[2] else None,
                ),
                logger=record.name,
                level=record.levelname,
                template=template,
                sample=_safe_message(record),
                when=record.created,
                detail=_full_text(record),
                source=_short_path(record.pathname, record.lineno),
                cause=_cause(record.exc_info[0], record.exc_info[1]) if record.exc_info and record.exc_info[0] else "",
            )
        except Exception:  # noqa: BLE001 - a log handler must never raise
            pass

    def add(
        self,
        *,
        domain: str | None,
        logger: str,
        level: str,
        template: str,
        sample: str,
        when: float,
        count: int = 1,
        detail: str = "",
        source: str = "",
        cause: str = "",
    ) -> None:
        # A counter or an address inside the text ("[2470414290096] Unexpected exception") is not another cause.
        template = _NUMBERS.sub("#", redact(template))
        sample = redact(sample)
        cause = " ".join(redact(cause).split())[:LOG_SAMPLE_LEN] if cause else ""
        detail = _clip(redact(detail)) if detail else ""
        key = (domain, logger, level, template[:200])
        hour = int(when // _HOUR)
        late = self.startup_until is not None and when > self.startup_until
        with self._lock:
            group = self._groups.get(key)
            if group is None:
                if len(self._groups) >= LOG_MAX_GROUPS:
                    oldest = min(self._groups, key=lambda k: self._groups[k].last_seen)
                    del self._groups[oldest]
                group = self._groups[key] = LogGroup(
                    domain, logger, level, template[:200], sample[:LOG_SAMPLE_LEN], when, when
                )
            group.hours[hour] = group.hours.get(hour, 0) + count
            if late:
                group.late[hour] = group.late.get(hour, 0) + count
            group.first_seen = min(group.first_seen, when)
            if when >= group.last_seen:
                group.last_seen = when
                group.sample = sample[:LOG_SAMPLE_LEN]
                if detail:
                    group.detail, group.source = detail, source[:200]
                if cause or detail:
                    group.cause = cause
            elif detail and not group.detail:
                group.detail, group.source, group.cause = detail, source[:200], cause

    def load(self, saved: list[dict], now: float | None = None) -> None:
        """Bring back the history saved before the last restart (already redacted when it was saved)."""
        keep_from = int(((now or time.time()) - LOG_HISTORY.total_seconds()) // _HOUR)
        with self._lock:
            for row in saved[:LOG_MAX_GROUPS]:
                try:
                    group = LogGroup(
                        row["domain"], row["logger"], row["level"], row["template"], row["sample"],
                        float(row["first"]), float(row["last"]),
                        {int(h): int(n) for h, n in row.get("hours", []) if int(h) >= keep_from},
                        {int(h): int(n) for h, n in row.get("late", []) if int(h) >= keep_from},
                        str(row.get("detail") or "")[:LOG_DETAIL_LEN], str(row.get("source") or "")[:200],
                        str(row.get("cause") or "")[:LOG_SAMPLE_LEN],
                    )
                except (KeyError, TypeError, ValueError):
                    continue
                if not group.hours:
                    continue
                # History saved by an older version: lines that differ only by a number become one line.
                group.template = _NUMBERS.sub("#", group.template)
                key = (group.domain, group.logger, group.level, group.template)
                known = self._groups.get(key)
                if known is None:
                    self._groups[key] = group
                    continue
                for hour, n in group.hours.items():
                    known.hours[hour] = known.hours.get(hour, 0) + n
                for hour, n in group.late.items():
                    known.late[hour] = known.late.get(hour, 0) + n
                known.first_seen = min(known.first_seen, group.first_seen)
                if group.last_seen > known.last_seen:
                    known.last_seen, known.sample = group.last_seen, group.sample
                    if group.detail:
                        known.detail, known.source, known.cause = group.detail, group.source, group.cause

    def saved(self) -> list[dict]:
        with self._lock:
            return [g.as_saved() for g in self._groups.values()]

    def take_system_log(self, hass: HomeAssistant, after: float = 0.0) -> None:
        """Copy the errors Home Assistant kept from before we started (its own system log).

        `after`: when the history was last saved. Older entries are in the history already (after a reload).
        """
        handler = hass.data.get("system_log")
        records = getattr(handler, "records", None)
        if records is None:
            return
        try:
            entries = records.to_list()
        except Exception:  # noqa: BLE001 - an internal of another integration; skip it if it changed
            return
        for entry in entries:
            try:
                if float(entry.get("timestamp") or 0) <= after:
                    continue
                source = entry.get("source") or ("", 0)
                message = entry.get("message") or [""]
                text = str(message[-1] if isinstance(message, list) else message)
                self.add(
                    domain=domain_of(
                        entry.get("name", ""), str(source[0]), _TB_FILE.findall(str(entry.get("exception") or ""))
                    ),
                    logger=entry.get("name", ""),
                    level=entry.get("level", "ERROR"),
                    template=text,
                    sample=text,
                    when=float(entry.get("timestamp") or time.time()),
                    count=int(entry.get("count") or 1),
                    detail="\n".join(
                        part for part in (
                            "\n".join(str(m) for m in message) if isinstance(message, list) else str(message),
                            str(entry.get("exception") or "").strip(),
                        ) if part
                    ),
                    source=_short_path(str(source[0]), source[1] if len(source) > 1 else 0),
                    cause=next(
                        (line.strip() for line in reversed(str(entry.get("exception") or "").splitlines()) if line.strip()), ""
                    ),
                )
            except Exception:  # noqa: BLE001
                continue

    def detail_of(self, key: str, now: float | None = None) -> dict | None:
        """The full text of one log line, by the key the report gave it. Only for the page of an admin."""
        since = (now or time.time()) - LOG_WINDOW.total_seconds()
        with self._lock:
            for group in self._groups.values():
                if f"log:{group.domain}:{group.template}" == key:
                    return {
                        "text": group.detail or group.sample,
                        "source": group.source,
                        "logger": group.logger,
                        "level": group.level,
                        "first": group.first_seen,
                        "last": group.last_seen,
                        "count": group.count(since),
                        "domain": group.domain,
                    }
        return None

    def groups(self, now: float | None = None) -> list[tuple[LogGroup, int]]:
        """The groups seen in the last 24 hours, with their counts, most first. History past 7 days is dropped."""
        now = now or time.time()
        since = now - LOG_WINDOW.total_seconds()
        keep_from = int((now - LOG_HISTORY.total_seconds()) // _HOUR)
        out: list[tuple[LogGroup, int]] = []
        with self._lock:
            for key in list(self._groups):
                group = self._groups[key]
                group.hours = {h: n for h, n in group.hours.items() if h >= keep_from}
                group.late = {h: n for h, n in group.late.items() if h >= keep_from}
                if not group.hours:
                    del self._groups[key]
                    continue
                count = group.count(since)
                if count:
                    out.append((group, count))
        out.sort(key=lambda gc: gc[1], reverse=True)
        return out


_NUMBERS = re.compile(r"\b(?:0x[0-9a-fA-F]{6,}|\d{6,})\b")
# Lines that only say "something failed here". The real error is the exception they carry.
_WRAPPER = re.compile(
    r"^(?:\[[^\]]{0,40}\]\s*)?(?:Error doing job|Unexpected exception|Task exception was never retrieved|"
    r"Exception in callback|Unhandled exception|Error handling (?:message|request)|Uncaught exception|Unexpected error)\b",
    re.I,
)


def is_wrapper(text: str) -> bool:
    return bool(_WRAPPER.match(text or ""))


def _cause(kind, error) -> str:
    """ "TimeoutError: no reply": the kind of the exception and its own words."""
    try:
        words = str(error) if error is not None else ""
    except Exception:  # noqa: BLE001
        words = ""
    name = getattr(kind, "__name__", "") or "Error"
    return f"{name}: {words}" if words else name


_PATH_TAIL = re.compile(r"(?:.*[/\\])?((?:custom_components|homeassistant|site-packages)[/\\].*)$")
_HOME_DIR = re.compile(r"(?:/(?:home|Users)/|[A-Za-z]:\\Users\\)[^/\\\s\"']+")


def _short_path(path: str | None, line: int | None = 0) -> str:
    """ "homeassistant/components/tuya/light.py:120": the end of the path that says which code it is."""
    if not path:
        return ""
    match = _PATH_TAIL.match(path)
    tail = (match.group(1) if match else path.replace("\\", "/").rsplit("/", 1)[-1]).replace("\\", "/")
    tail = tail.removeprefix("site-packages/")
    return f"{tail}:{line}" if line else tail


def _clip(text: str) -> str:
    """Home folders (they hold a user name) are shortened, and a long text keeps its start and its end."""
    text = _HOME_DIR.sub("~", text).strip()
    if len(text) <= LOG_DETAIL_LEN:
        return text
    half = LOG_DETAIL_LEN // 2 - 10
    return f"{text[:half]}\n…\n{text[-half:]}"


def _full_text(record: logging.LogRecord) -> str:
    """The whole message and, when there is one, its traceback."""
    try:
        text = record.getMessage()
    except Exception:  # noqa: BLE001
        text = str(record.msg)
    if record.exc_info and record.exc_info[0] is not None:
        try:
            text = f"{text}\n{''.join(traceback.format_exception(*record.exc_info)).strip()}"
        except Exception:  # noqa: BLE001
            pass
    return text


def _safe_message(record: logging.LogRecord) -> str:
    try:
        text = record.getMessage()
    except Exception:  # noqa: BLE001
        text = str(record.msg)
    return " ".join(text.split())
