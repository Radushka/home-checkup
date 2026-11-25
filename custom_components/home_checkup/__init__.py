"""Home Checkup: a calm daily checkup of a Home Assistant home, in plain words.

It reads the log, the registries and the configuration, and lists what needs a look.
It only reads. It never changes, removes or restarts anything. The full report is a page in the sidebar.
"""

from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from .checkup import Checkup
from .const import DOMAIN
from .panel import async_add_panel, async_remove_panel
from .websocket import async_register_commands

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
PLATFORMS = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async_register_commands(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    started_at: datetime | None = None if hass.state is not CoreState.running else _guess_start(hass)
    checkup = Checkup(hass, started_at)
    checkup.apply_settings(dict(entry.options), started=False)
    await checkup.async_start()
    entry.runtime_data = checkup
    hass.data[DOMAIN] = checkup
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_add_panel(hass)
    entry.async_on_unload(entry.add_update_listener(_options_changed))
    return True


async def _options_changed(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """A changed setting applies at once, with no reload."""
    checkup = entry.runtime_data
    checkup.apply_settings(dict(entry.options))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        async_remove_panel(hass)
        entry.runtime_data.async_stop()
        hass.data.pop(DOMAIN, None)
    return ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Removing Home Checkup also removes its notes in Repairs."""
    from .repairs import async_clear_all

    async_clear_all(hass)


def _guess_start(hass: HomeAssistant) -> datetime:
    """After a reload we did not see the start; the oldest state change is a close, safe guess."""
    oldest = min((s.last_changed for s in hass.states.async_all()), default=None)
    return oldest or dt_util.utcnow()
