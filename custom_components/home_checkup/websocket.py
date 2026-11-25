"""Websocket commands. The full report is sent only when someone opens it, so tablets stay light."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from homeassistant.loader import async_get_loaded_integration

from .const import DOMAIN
from .fixes import FIX_KINDS, FixError


@callback
def async_register_commands(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_report)
    websocket_api.async_register_command(hass, ws_scan)
    websocket_api.async_register_command(hass, ws_keep)
    websocket_api.async_register_command(hass, ws_acted)
    websocket_api.async_register_command(hass, ws_log_detail)
    for command in (
        ws_fix_plan,
        ws_fix_entities,
        ws_fix_undo,
        ws_fix_device,
        ws_fix_area,
        ws_reload_entry,
        ws_fix_helpers_start,
        ws_fix_helpers_finish,
        ws_fix_helpers_saved,
        ws_fix_automation_start,
        ws_fix_automation_finish,
        ws_fix_automation_saved,
    ):
        websocket_api.async_register_command(hass, command)


def _checkup(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]):
    checkup = hass.data.get(DOMAIN)
    if checkup is None:
        connection.send_error(msg["id"], "not_loaded", "Home Checkup is not set up.")
    return checkup


# The full report names integrations, automations, files and log lines: it is for admins only.
# Everyone else (a wall tablet, a family account) reads the sensor: the count, the headline and the group names.
@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/report"})
@callback
def ws_report(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    if checkup := _checkup(hass, connection, msg):
        connection.send_result(msg["id"], _report(checkup, connection))


def _report(checkup, connection: websocket_api.ActiveConnection) -> dict[str, Any]:
    """The report with the recent fixes (with Undo). Every command that sends it is for admins only."""
    report = checkup.report()
    report["fixes"] = checkup.fixes.recent()
    return report


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/scan"})
@websocket_api.async_response
async def ws_scan(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    if checkup := _checkup(hass, connection, msg):
        await checkup.async_full_scan()
        connection.send_result(msg["id"], _report(checkup, connection))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/acted",
        vol.Required("integration"): vol.All(str, vol.Length(max=100)),
        vol.Required("action"): vol.In(("update", "signin", "devices", "template", "logs")),
    }
)
@websocket_api.async_response
async def ws_acted(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """The page tells Home Checkup that someone took a log next step, so it can say later if it worked."""
    if checkup := _checkup(hass, connection, msg):
        await checkup.async_acted(msg["integration"], msg["action"])
        connection.send_result(msg["id"], {})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/keep",
        vol.Exclusive("key", "what"): vol.All(str, vol.Length(min=1, max=500)),
        # "Ignore all" of one group, and its Undo: many items in one step.
        vol.Exclusive("keys", "what"): vol.All([vol.All(str, vol.Length(min=1, max=500))], vol.Length(min=1, max=500)),
        vol.Optional("keep", default=True): bool,
    }
)
@websocket_api.async_response
async def ws_keep(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Mark an item "Keep" (it never shows again), or take the mark away. This changes only our own list."""
    keys = msg.get("keys") or ([msg["key"]] if "key" in msg else [])
    if not keys:
        connection.send_error(msg["id"], "invalid_format", "key or keys is needed")
        return
    if checkup := _checkup(hass, connection, msg):
        await checkup.async_set_keep(keys, msg["keep"])
        connection.send_result(msg["id"], _report(checkup, connection))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/log_detail", vol.Required("key"): vol.All(str, vol.Length(min=1, max=500))}
)
@callback
def ws_log_detail(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """The full text of one log line (already redacted), for the person who opens it. Nothing leaves the home."""
    if checkup := _checkup(hass, connection, msg):
        detail = checkup.watch.detail_of(msg["key"])
        if detail is None:
            connection.send_error(msg["id"], "not_found", "This line is no longer in the log.")
        else:
            detail.update(_about(hass, detail.pop("domain", None), detail["text"]))
            connection.send_result(msg["id"], detail)


_IN_CODE = re.compile(r"(custom_components|homeassistant/components)/([a-z0-9_]+)/")


def _about(hass: HomeAssistant, domain: str | None, text: str) -> dict[str, Any]:
    """Facts for a person who troubleshoots: which integration, its version, where its known issues are.

    When Home Assistant itself logged the error, the last integration named in the error text is the likely source.
    """
    seen = ""
    if not domain:
        found = _IN_CODE.findall(text or "")
        custom = [name for kind, name in found if kind == "custom_components" and name != DOMAIN]
        seen = (custom or [name for _, name in found if name != DOMAIN] or [""])[-1]
    name = version = issues = ""
    built_in = True
    target = domain or seen
    if target:
        try:
            integration = async_get_loaded_integration(hass, target)
        except Exception:  # noqa: BLE001 - not loaded, or not an integration
            if not domain:
                return {"integration": "", "version": "", "issues": "", "page": "", "likely": False}
            name = target
        else:
            name = integration.name
            built_in = integration.is_built_in
            version = "" if built_in else str(integration.version or "")
            issues = str(integration.issue_tracker or "")
            if built_in and not issues:
                issues = f"https://github.com/home-assistant/core/issues?q=is%3Aissue+is%3Aopen+label%3A%22integration%3A+{target}%22"
    if not issues.startswith("https://"):
        issues = ""
    return {
        "integration": name,
        "version": version,
        "issues": issues,
        "page": f"/config/integrations/integration/{target}" if target else "",
        "likely": bool(seen),
    }


# ---- safe fixes (admins only). Each one: exact list first, backup, then the change, then a count. ----------------


async def _fix(hass, connection, msg, work) -> None:
    if not (checkup := _checkup(hass, connection, msg)):
        return
    try:
        result = await work(checkup)
    except FixError as err:
        connection.send_error(msg["id"], "fix_failed", str(err))
        return
    checkup.refresh()
    connection.send_result(msg["id"], {"fix": result, "report": _report(checkup, connection)})


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/fix_plan", vol.Required("kind"): vol.In(FIX_KINDS)})
@callback
def ws_fix_plan(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """The exact list a fix would act on. Nothing changes."""
    if checkup := _checkup(hass, connection, msg):
        try:
            connection.send_result(msg["id"], checkup.fixes.plan(msg["kind"], checkup.findings))
        except FixError as err:
            connection.send_error(msg["id"], "fix_failed", str(err))


_KEYS = vol.All([vol.All(str, vol.Length(min=1, max=500))], vol.Length(min=1, max=2000))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/fix_entities", vol.Required("plan_id"): str, vol.Required("keys"): _KEYS}
)
@websocket_api.async_response
async def ws_fix_entities(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    await _fix(hass, connection, msg, lambda c: c.fixes.async_remove_entities(msg["plan_id"], msg["keys"]))


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/fix_device", vol.Required("key"): str})
@websocket_api.async_response
async def ws_fix_device(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    await _fix(hass, connection, msg, lambda c: c.fixes.async_disable_device(msg["key"], c.findings))


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/fix_area", vol.Required("key"): str})
@websocket_api.async_response
async def ws_fix_area(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    await _fix(hass, connection, msg, lambda c: c.fixes.async_set_area(msg["key"], c.findings))


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/reload_entry", vol.Required("key"): str})
@websocket_api.async_response
async def ws_reload_entry(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Reload one integration that did not start, the way Home Assistant's own menu does. Nothing is deleted."""
    if checkup := _checkup(hass, connection, msg):
        started = await checkup.async_reload_entry(msg["key"])
        checkup.refresh()
        connection.send_result(msg["id"], {"started": started, "report": _report(checkup, connection)})


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/fix_undo", vol.Required("fix_id"): str})
@websocket_api.async_response
async def ws_fix_undo(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    await _fix(hass, connection, msg, lambda c: c.fixes.async_undo(msg["fix_id"]))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/fix_helpers_start",
        vol.Required("plan_id"): str,
        vol.Required("keys"): _KEYS,
        vol.Required("saved"): [dict],
    }
)
@websocket_api.async_response
async def ws_fix_helpers_start(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Before the page removes helpers: check the list and write the backup."""
    await _fix(hass, connection, msg, lambda c: c.fixes.async_record_helpers(msg["plan_id"], msg["keys"], msg["saved"]))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/fix_helpers_finish", vol.Required("fix_id"): str, vol.Optional("undo", default=False): bool}
)
@websocket_api.async_response
async def ws_fix_helpers_finish(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    await _fix(hass, connection, msg, lambda c: c.fixes.async_finish_helpers(msg["fix_id"], msg["undo"]))


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/fix_helpers_saved", vol.Required("fix_id"): str})
@callback
def ws_fix_helpers_saved(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """The saved helper settings, so the page can bring them back with Home Assistant's own helper commands."""
    if checkup := _checkup(hass, connection, msg):
        try:
            connection.send_result(msg["id"], checkup.fixes.helper_backup(msg["fix_id"]))
        except FixError as err:
            connection.send_error(msg["id"], "fix_failed", str(err))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/fix_automation_start",
        vol.Required("key"): vol.All(str, vol.Length(min=1, max=500)),
        vol.Optional("before"): dict,
        vol.Optional("new"): str,
    }
)
@websocket_api.async_response
async def ws_fix_automation_start(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Before the page fixes a broken automation step: check, back up, record. Returns what to change."""
    if not (checkup := _checkup(hass, connection, msg)):
        return
    try:
        fix = await checkup.fixes.async_record_automation(
            checkup.findings, msg["key"], msg.get("before"), msg.get("new")
        )
    except FixError as err:
        connection.send_error(msg["id"], "fix_failed", str(err))
        return
    connection.send_result(msg["id"], {"fix": fix})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/fix_automation_finish", vol.Required("fix_id"): str, vol.Optional("undo", default=False): bool}
)
@websocket_api.async_response
async def ws_fix_automation_finish(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    await _fix(hass, connection, msg, lambda c: c.fixes.async_finish_automation(msg["fix_id"], msg["undo"]))


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/fix_automation_saved", vol.Required("fix_id"): str})
@callback
def ws_fix_automation_saved(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """What Undo needs to put the automation back."""
    if checkup := _checkup(hass, connection, msg):
        try:
            connection.send_result(msg["id"], checkup.fixes.automation_backup(msg["fix_id"]))
        except FixError as err:
            connection.send_error(msg["id"], "fix_failed", str(err))
