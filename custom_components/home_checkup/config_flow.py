"""Adding Home Checkup from Settings > Devices & services, and its one setting."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback

from .checkup import letter_places
from .const import CONF_REPAIRS_NOTE, CONF_WEEKLY_LETTER, DOMAIN, NAME


class HomeCheckupFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title=NAME, data={})
        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return HomeCheckupOptions()


class HomeCheckupOptions(OptionsFlow):
    """Two settings: the one note in Repairs, and where the weekly letter is sent (off until chosen)."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            # The other settings live behind the gear on the page: they are kept.
            return self.async_create_entry(data={**self.config_entry.options, **user_input})
        current = self.config_entry.options.get(CONF_REPAIRS_NOTE, True)
        letter = self.config_entry.options.get(CONF_WEEKLY_LETTER, "off")
        # Only the names of the notify services that exist here. Nothing is sent until one is chosen.
        places = letter_places(self.hass)
        if letter not in places:
            letter = "off"
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_REPAIRS_NOTE, default=current): bool,
                    vol.Required(CONF_WEEKLY_LETTER, default=letter): vol.In(places),
                }
            ),
        )
