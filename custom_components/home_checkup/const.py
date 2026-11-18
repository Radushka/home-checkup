"""Names and limits shared by the Home Checkup files."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "home_checkup"
NAME = "Home Checkup"

# The page in the sidebar (admins only) and where its one script is served from.
PANEL_URL = "home-checkup"
PANEL_ICON = "mdi:heart-pulse"
PANEL_ELEMENT = "home-checkup-panel"
STATIC_URL = "/home_checkup_static"

# Setting: show one note in Repairs when something needs a look (on by default).
CONF_REPAIRS_NOTE = "repairs_note"

# When the full checkup runs: once a day at this local time, and once a few minutes after Home Assistant starts.
DAILY_HOUR = 8
FIRST_SCAN_DELAY = 300  # seconds after start, so integrations have time to come up
REFRESH_EVERY = timedelta(hours=1)  # cheap refresh of the log part and the registries

LOG_WINDOW = timedelta(hours=24)
LOG_HISTORY = timedelta(days=7)  # kept (on disk, redacted) so errors that keep coming back are seen across restarts
STARTUP_GRACE = 300  # seconds after Home Assistant says it started; errors before that are "start-up noise"
STOPPED_AFTER = timedelta(hours=6)  # quiet this long after you acted: "the errors stopped"
STOPPED_SHOWN = timedelta(days=3)  # how long "the errors stopped" stays on the page
NEW_ERROR_AFTER = timedelta(days=2)  # watched this long, a brand new error goes in the note at once
LOG_MAX_GROUPS = 300
LOG_SAMPLE_LEN = 300
LOG_DETAIL_LEN = 4000  # the full text of the newest error of a group (redacted), shown when the person opens the line

UNAVAILABLE_AFTER = timedelta(days=7)
UNAVAILABLE_SINCE_START_AFTER = timedelta(days=1)
HELPER_MIN_AGE = timedelta(days=7)
BATTERY_LOW = 15  # percent
NOTE_HOURS = 3  # a log error goes in the Repairs note when seen in this many different hours of the last 24
NEW_FOR = timedelta(hours=24)  # an item is marked "New" for this long after it first shows

# Helpers a person makes by hand. Only these are checked for "nothing uses it".
HELPER_DOMAINS = (
    "input_boolean",
    "input_button",
    "input_datetime",
    "input_number",
    "input_select",
    "input_text",
    "counter",
    "timer",
    "schedule",
)

# Files read (never changed) to see which helpers are used somewhere.
# Only helper ids (like input_boolean.guest_mode) are picked out of them; no other text is kept.
# Never read: secrets.yaml, anything named like a secret or key file, and Home Assistant's .storage files that
# hold sign-ins (core.config_entries, auth, cloud, application credentials). Only dashboard files are read there.
CORPUS_MAX_BYTES = 50 * 1024 * 1024
CORPUS_SKIP_DIRS = {
    ".storage", ".git", "deps", "custom_components", "www", "backups", "tts",
    "node_modules", "home_checkup_backups", ".cloud", "blueprints",
}
CORPUS_SKIP_NAME_PARTS = ("secret", "credential", "password", "token", "private", ".env")
CORPUS_STORAGE_PREFIXES = ("lovelace", "hadash")

# Helper-style integrations whose settings are templates or entity choices (never sign-ins).
# Their settings are checked in memory, and only their "options", never their "data", where keys live.
TEMPLATE_HELPER_DOMAINS = (
    "template", "group", "threshold", "derivative", "utility_meter", "statistics", "min_max",
    "switch_as_x", "trend", "filter", "history_stats", "integration", "tod", "generic_thermostat",
    "generic_hygrostat", "mold_indicator", "random", "combined_energy",
)
