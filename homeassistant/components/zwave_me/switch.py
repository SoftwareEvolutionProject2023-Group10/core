"""Representation of a switchBinary."""
import logging
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ZWaveMeEntity
from .const import ZWaveMePlatform
from .helpers import setup_entry

_LOGGER = logging.getLogger(__name__)
DEVICE_NAME = ZWaveMePlatform.SWITCH

SWITCH_MAP: dict[str, SwitchEntityDescription] = {
    "generic": SwitchEntityDescription(
        key="generic",
        device_class=SwitchDeviceClass.SWITCH,
    )
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    setup_entry(
        hass,
        config_entry,
        async_add_entities,
        DEVICE_NAME,
        ZWaveMeSwitch,
        lambda new_device: [
            SWITCH_MAP["generic"],
        ],
    )


class ZWaveMeSwitch(ZWaveMeEntity, SwitchEntity):
    """Representation of a ZWaveMe binary switch."""

    def __init__(self, controller, device, description):
        """Initialize the device."""
        super().__init__(controller, device)
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self.device.level == "on"

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self.controller.zwave_api.send_command(self.device.id, "on")

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        self.controller.zwave_api.send_command(self.device.id, "off")
