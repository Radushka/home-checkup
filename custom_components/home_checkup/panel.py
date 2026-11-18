"""The Home Checkup page in the sidebar: the full report, for admins only.

It is one small script with no outside parts, served from this folder. It only reads the report and changes
Home Checkup's own "Keep" list; it never changes the home.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from homeassistant.core import HomeAssistant

from .const import DOMAIN, PANEL_ELEMENT, PANEL_ICON, PANEL_URL, STATIC_URL

_LOGGER = logging.getLogger(__name__)
_FOLDER = Path(__file__).parent / "frontend"
_STATIC_DONE = f"{DOMAIN}_static_registered"


def _version() -> str:
    return json.loads((Path(__file__).parent / "manifest.json").read_text())["version"]


async def async_add_panel(hass: HomeAssistant) -> bool:
    """Add the sidebar page. Returns False (and the rest still works) when the frontend is not loaded."""
    if "frontend" not in hass.config.components or getattr(hass, "http", None) is None:
        return False
    from homeassistant.components import panel_custom
    from homeassistant.components.http import StaticPathConfig

    if not hass.data.get(_STATIC_DONE):
        await hass.http.async_register_static_paths([StaticPathConfig(STATIC_URL, str(_FOLDER), False)])
        hass.data[_STATIC_DONE] = True
    version = await hass.async_add_executor_job(_version)
    try:
        await panel_custom.async_register_panel(
            hass,
            frontend_url_path=PANEL_URL,
            webcomponent_name=PANEL_ELEMENT,
            sidebar_title="Home Checkup",
            sidebar_icon=PANEL_ICON,
            module_url=f"{STATIC_URL}/home-checkup-panel.js?v={version}",
            require_admin=True,
        )
    except ValueError:  # already there, for example after a quick reload
        _LOGGER.debug("Home Checkup page was already in the sidebar")
    return True


def async_remove_panel(hass: HomeAssistant) -> None:
    if "frontend" not in hass.config.components:
        return
    from homeassistant.components import frontend

    frontend.async_remove_panel(hass, PANEL_URL, warn_if_unknown=False)
