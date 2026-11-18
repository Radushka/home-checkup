"""One small sensor: the number of things that need a look (0 = healthy). Dashboards and tablets read only this."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .checkup import Checkup
from .const import DOMAIN, NAME

MAX_LISTED = 10


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([HomeCheckupSensor(entry.runtime_data, entry.entry_id)])


class HomeCheckupSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "checkup"
    _attr_icon = "mdi:home-heart"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_should_poll = False
    # The short list changes often and is not useful in history; keep the database small.
    _unrecorded_attributes = frozenset({"findings", "summary"})

    def __init__(self, checkup: Checkup, entry_id: str) -> None:
        self._checkup = checkup
        self._attr_unique_id = f"{entry_id}_checkup"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)}, name=NAME, entry_type=DeviceEntryType.SERVICE
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._checkup.add_listener(self.async_write_ha_state))

    @property
    def native_value(self) -> int:
        return self._checkup.count

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        checkup = self._checkup
        return {
            "status": "healthy" if checkup.count == 0 else "attention",
            "headline": checkup.headline,
            "summary": checkup.summary()[:MAX_LISTED],
            "findings": [
                {
                    "kind": f.kind,
                    "title": f.title,
                    "severity": f.severity,
                    "count": len(f.items),
                    "integration": f.integration,
                    "integration_name": f.integration_name,
                }
                for f in checkup.findings[:MAX_LISTED]
            ],
            "scanned_at": checkup.scanned_at.isoformat() if checkup.scanned_at else None,
        }
