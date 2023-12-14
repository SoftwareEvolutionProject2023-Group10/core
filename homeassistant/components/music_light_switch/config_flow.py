"""Config flow to configure a light switcher."""

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.const import CONF_LIGHTS
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN, LIGHT_IDS, MEDIA_PLAYER_ENTITY_ID

CONF_MEDIA_PLAYER = "media_player"


def _dataSchema(defaults=None):
    if defaults is None:
        defaults = {}

    return vol.Schema(
        {
            vol.Required(
                CONF_MEDIA_PLAYER,
                default=defaults.get(MEDIA_PLAYER_ENTITY_ID, ""),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=[MEDIA_PLAYER_DOMAIN],
                )
            ),
            vol.Required(
                CONF_LIGHTS,
                default=defaults.get(LIGHT_IDS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=[LIGHT_DOMAIN],
                    multiple=True,
                )
            ),
        }
    )


class MusicLightSwitchOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle music light switch option changes."""

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
                    MEDIA_PLAYER_ENTITY_ID: user_input.get(CONF_MEDIA_PLAYER),
                    LIGHT_IDS: user_input.get(CONF_LIGHTS),
                },
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_dataSchema(self.config_entry.options),
        )


class MusicLightSwitchFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Create a music light switch with initial options."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> MusicLightSwitchOptionsFlowHandler:
        """Get the options flow for this handler."""
        return MusicLightSwitchOptionsFlowHandler(config_entry)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized when adding a new music light switch."""
        return await self.async_step_user(user_input)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(
                title="Music light switch",
                data={},
                options={
                    MEDIA_PLAYER_ENTITY_ID: user_input.get(CONF_MEDIA_PLAYER),
                    LIGHT_IDS: user_input.get(CONF_LIGHTS),
                },
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_dataSchema(),
        )
