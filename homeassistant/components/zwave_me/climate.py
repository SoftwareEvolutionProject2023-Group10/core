"""Representation of a thermostat."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ZWaveMeEntity
from .const import ZWaveMePlatform
from .helpers import setup_entry

TEMPERATURE_DEFAULT_STEP = 0.5

DEVICE_NAME = ZWaveMePlatform.CLIMATE


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the climate platform."""
    setup_entry(hass, config_entry, async_add_entities, DEVICE_NAME, ZWaveMeClimate)


class ZWaveMeClimate(ZWaveMeEntity, ClimateEntity):
    """Representation of a ZWaveMe sensor."""

    _attr_hvac_mode = HVACMode.HEAT
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        self.controller.zwave_api.send_command(
            self.device.id, f"exact?level={temperature}"
        )

    @property
    def temperature_unit(self) -> str:
        """Return the temperature_unit."""
        return self.device.scaleTitle

    @property
    def target_temperature(self) -> float:
        """Return the state of the sensor."""
        return self.device.level

    @property
    def max_temp(self) -> float:
        """Return min temperature for the device."""
        return self.device.max

    @property
    def min_temp(self) -> float:
        """Return max temperature for the device."""
        return self.device.min

    @property
    def target_temperature_step(self) -> float:
        """Return the supported step of target temperature."""
        return TEMPERATURE_DEFAULT_STEP
