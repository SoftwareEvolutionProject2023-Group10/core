"""Config flow to configure a light switcher."""

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN
from homeassistant.const import CONF_LIGHTS
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN

CONF_WEATHER = "weather_service"


def _dataSchema(defaults=None):
    if defaults is None:
        defaults = {}

    return vol.Schema(
        {
            vol.Required(
                CONF_WEATHER,
                default=defaults.get("weather_entity_id", ""),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=[WEATHER_DOMAIN],
                )
            ),
            vol.Required(
                CONF_LIGHTS,
                default=defaults.get("light_ids", []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=[LIGHT_DOMAIN],
                    multiple=True,
                )
            ),
        }
    )


class WeatherLightSwitchOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle weather light switch option changes."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the option flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a change request by the user."""
        if user_input is not None:
            return self.async_create_entry(
                data={
                    "weather_entity_id": user_input.get(CONF_WEATHER),
                    "light_ids": user_input.get(CONF_LIGHTS),
                },
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_dataSchema(self.config_entry.options),
        )


class WeatherLightSwitchFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Create a weather light switch with initial options."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> WeatherLightSwitchOptionsFlowHandler:
        """Get the options flow for this handler."""
        return WeatherLightSwitchOptionsFlowHandler(config_entry)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized when adding a new weather light switch."""
        return await self.async_step_user(user_input)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(
                title="Weather light switch",
                data={},
                options={
                    "weather_entity_id": user_input.get(CONF_WEATHER),
                    "light_ids": user_input.get(CONF_LIGHTS),
                },
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_dataSchema(),
        )
