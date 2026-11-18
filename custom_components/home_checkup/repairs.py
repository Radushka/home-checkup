"""One calm note in Home Assistant's own Repairs page, so people who never open a dashboard still see it.

Repairs is Home Assistant's place for real problems, shared with every other integration. Home Checkup adds at
most ONE note there ("Home Checkup: 3 things need a look"), never one per kind or per item. The full list lives
on the Home Checkup page in the sidebar. The note shows only for "warning" findings and goes away by itself
when nothing needs a look.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN, PANEL_URL

ISSUE_ID = "checkup"

# Many people never open their log, so log errors do go in the note, but only the ones that keep coming back
# (see checks.check_log: in_note). One short burst stays on the Home Checkup page only, so the note is not noise.

# Version 0.1 made one note per kind. They are removed on the first scan after an update.
OLD_KINDS = (
    "failed_integrations",
    "log_errors",
    "broken_references",
    "leftover_entities",
    "leftover_devices",
    "unavailable",
)


@callback
def async_sync_issues(hass: HomeAssistant, findings: list) -> None:
    for kind in OLD_KINDS:
        ir.async_delete_issue(hass, DOMAIN, kind)
    # Home Assistant's own repairs come first: a problem of an integration that already has its own note
    # there is not counted again in ours (it is still on the Home Checkup page).
    covered = {
        issue.domain
        for issue in ir.async_get(hass).issues.values()
        if issue.domain != DOMAIN and issue.active and issue.dismissed_version is None
    }
    warnings = [
        f
        for f in findings
        if f.severity == "warning"
        and f.in_note
        and not (f.integration and f.integration in covered)
    ]
    if not warnings:
        ir.async_delete_issue(hass, DOMAIN, ISSUE_ID)
        return
    shown = warnings[:5]
    more = len(warnings) - len(shown)
    lines = [f"- {f.title}" for f in shown] + ([f"- and {more} more"] if more else [])
    ir.async_create_issue(
        hass,
        DOMAIN,
        ISSUE_ID,
        is_fixable=False,
        is_persistent=False,
        severity=ir.IssueSeverity.WARNING,
        learn_more_url=f"homeassistant://{PANEL_URL}",  # opens the sidebar page inside Home Assistant
        translation_key="things_to_look_at" if len(warnings) > 1 else "thing_to_look_at",
        translation_placeholders={"count": str(len(warnings)), "list": "\n".join(lines)},
    )


@callback
def async_clear_all(hass: HomeAssistant) -> None:
    for issue_id in (ISSUE_ID, *OLD_KINDS):
        ir.async_delete_issue(hass, DOMAIN, issue_id)
