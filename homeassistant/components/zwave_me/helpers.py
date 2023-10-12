"""Helpers for zwave_me config flow."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from zwave_me_ws import ZWaveMe, ZWaveMeData

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ZWaveMeController
from .const import DOMAIN


async def get_uuid(url: str, token: str | None = None) -> str | None:
    """Get an uuid from Z-Wave-Me."""
    conn = ZWaveMe(url=url, token=token)
    uuid = None
    if await conn.get_connection():
        uuid = await conn.get_uuid()
    await conn.close_ws()
    return uuid


def setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    device_name: str,
    device_constructor: Callable[..., Entity],
    constructor_args: Callable[[ZWaveMeData], list[Any]] = lambda new_device: [],
) -> None:
    """Set up a new device entry."""

    @callback
    def add_new_device(new_device: ZWaveMeData) -> None:
        """Add a new device."""
        controller: ZWaveMeController = hass.data[DOMAIN][config_entry.entry_id]
        device = device_constructor(
            controller, new_device, *constructor_args(new_device)
        )

        async_add_entities(
            [
                device,
            ]
        )

    config_entry.async_on_unload(
        async_dispatcher_connect(
            hass, f"ZWAVE_ME_NEW_{device_name.upper()}", add_new_device
        )
    )
