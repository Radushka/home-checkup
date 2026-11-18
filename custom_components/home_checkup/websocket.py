"""Websocket commands. The full report is sent only when someone opens it, so tablets stay light."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .fixes import FIX_KINDS, FixError


@callback
def async_register_commands(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_report)
    websocket_api.async_register_command(hass, ws_scan)
    websocket_api.async_register_command(hass, ws_keep)
    websocket_api.async_register_command(hass, ws_acted)
    for command in (
        ws_fix_plan,
        ws_fix_entities,
        ws_fix_undo,
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


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/report"})
@callback
def ws_report(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    if checkup := _checkup(hass, connection, msg):
        connection.send_result(msg["id"], _report(checkup, connection))


def _report(checkup, connection: websocket_api.ActiveConnection) -> dict[str, Any]:
    """The report; admins also get the recent fixes (with Undo)."""
    report = checkup.report()
    if connection.user and connection.user.is_admin:
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
        vol.Required("key"): vol.All(str, vol.Length(min=1, max=500)),
        vol.Optional("keep", default=True): bool,
    }
)
@websocket_api.async_response
async def ws_keep(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Mark an item "Keep" (it never shows again), or take the mark away. This changes only our own list."""
    if checkup := _checkup(hass, connection, msg):
        await checkup.async_set_keep(msg["key"], msg["keep"])
        connection.send_result(msg["id"], _report(checkup, connection))


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
