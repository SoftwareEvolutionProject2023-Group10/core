"""Representation of a sensorBinary."""
from __future__ import annotations

from zwave_me_ws import ZWaveMeData

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ZWaveMeController, ZWaveMeEntity
from .const import GENERIC, ZWaveMePlatform
from .helpers import setup_entry

BINARY_SENSORS_MAP: dict[str, BinarySensorEntityDescription] = {
    GENERIC: BinarySensorEntityDescription(
        key=GENERIC,
    ),
    "motion": BinarySensorEntityDescription(
        key="motion",
        device_class=BinarySensorDeviceClass.MOTION,
    ),
}
DEVICE_NAME = ZWaveMePlatform.BINARY_SENSOR


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    setup_entry(
        hass,
        config_entry,
        async_add_entities,
        DEVICE_NAME,
        ZWaveMeBinarySensor,
        lambda new_device: [
            BINARY_SENSORS_MAP.get(new_device.probeType, BINARY_SENSORS_MAP[GENERIC]),
        ],
    )


class ZWaveMeBinarySensor(ZWaveMeEntity, BinarySensorEntity):
    """Representation of a ZWaveMe binary sensor."""

    def __init__(
        self,
        controller: ZWaveMeController,
        device: ZWaveMeData,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the device."""
        super().__init__(controller=controller, device=device)
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        return self.device.level == "on"
