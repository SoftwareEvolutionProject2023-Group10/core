"""The template component."""
from __future__ import annotations

import asyncio
from collections.abc import Callable
import logging

import voluptuous as vol

from homeassistant import config as conf_util
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_UNIQUE_ID,
    EVENT_HOMEASSISTANT_START,
    SERVICE_RELOAD,
)
from homeassistant.core import (
    CoreState,
    Event,
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import (
    discovery,
    trigger as trigger_helper,
    update_coordinator,
)
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_track_state_change_event,
)
from homeassistant.helpers.reload import async_reload_integration_platforms
from homeassistant.helpers.script import Script
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.helpers.typing import ConfigType, EventType
from homeassistant.loader import async_get_integration

from .const import CONF_ACTION, CONF_TRIGGER, DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the template integration."""
    if DOMAIN in config:
        await _process_config(hass, config)

    async def _reload_config(call: Event | ServiceCall) -> None:
        """Reload top-level + platforms."""
        try:
            unprocessed_conf = await conf_util.async_hass_config_yaml(hass)
        except HomeAssistantError as err:
            _LOGGER.error(err)
            return

        conf = await conf_util.async_process_component_config(
            hass, unprocessed_conf, await async_get_integration(hass, DOMAIN)
        )

        if conf is None:
            return

        await async_reload_integration_platforms(hass, DOMAIN, PLATFORMS)

        if DOMAIN in conf:
            await _process_config(hass, conf)

        hass.bus.async_fire(f"event_{DOMAIN}_reloaded", context=call.context)

    async def _weather_service_call(call: ServiceCall) -> ServiceResponse:
        if call.data.get("main") is None:
            weather_type = "Cloudy"
        else:
            weather_type = call.data["main"]

        # The light that we have
        light_entity_id = "light.simulated_light"

        # Assuming the weather platform is named "weather.home"
        weather_entity_id = "weather.simulated_weather"

        # Get the weather state object
        weather_state = hass.states.get(weather_entity_id)

        if weather_state is not None:
            # Get the current weather condition
            pass
        else:
            # Default to "Cloudy" if weather state is not available
            pass

        # Define the RGB color based on your weather type (replace this with your logic)
        if weather_type == "Sunny":
            rgb_color = [255, 255, 0]  # Example: Yellow color
        elif weather_type == "Rainy":
            rgb_color = [0, 0, 255]  # Example: Blue color
        else:
            rgb_color = [50, 168, 82]  # Default: Green color
        hass.bus.async_fire("custom_event", {"rgb": rgb_color})

        # Call to turn the light on
        await hass.services.async_call(
            "light",
            "turn_on",
            {
                "entity_id": light_entity_id,
                "rgb_color": rgb_color,
            },
        )

        return {"main": weather_type, "rgb": str(rgb_color)}

    async def _weather_service_turn_off(_: ServiceCall):
        # The light that we have
        light_entity_id = "light.simulated_light"
        await hass.services.async_call(
            "light",
            "turn_off",
            {
                "entity_id": light_entity_id,
            },
        )
        hass.bus.async_fire("custom_event", {"rgb": [128, 128, 128]})  # Gray color

    # Register the services
    async_register_admin_service(
        hass, domain=DOMAIN, service=SERVICE_RELOAD, service_func=_reload_config
    )
    hass.services.async_register(
        domain=DOMAIN,
        service="weather_service",
        service_func=_weather_service_call,
        schema=vol.Schema(
            {
                vol.Optional("main"): str,
            }
        ),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        domain=DOMAIN,
        service="weather_service_turn_off",
        service_func=_weather_service_turn_off,
    )

    @callback
    async def update_lights_weather(event: EventType[EventStateChangedData]) -> None:
        """Call back for update of the weather."""

        # The light that we have
        light_entity_id = "light.simulated_light"
        color = (0, 0, 0)
        await hass.services.async_call(
            "light",
            "turn_on",
            {
                "entity_id": light_entity_id,
                "rgb_color": color,
            },
        )
        hass.bus.async_fire("custom_event", {"rgb": color})

    async_track_state_change_event(
        hass, ["weather.smhi_weather"], update_lights_weather
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    await hass.config_entries.async_forward_entry_setups(
        entry, (entry.options["template_type"],)
    )
    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))
    return True


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(
        entry, (entry.options["template_type"],)
    )


async def _process_config(hass: HomeAssistant, hass_config: ConfigType) -> None:
    """Process config."""
    coordinators: list[TriggerUpdateCoordinator] | None = hass.data.pop(DOMAIN, None)

    # Remove old ones
    if coordinators:
        for coordinator in coordinators:
            coordinator.async_remove()

    async def init_coordinator(hass, conf_section):
        coordinator = TriggerUpdateCoordinator(hass, conf_section)
        await coordinator.async_setup(hass_config)
        return coordinator

    coordinator_tasks = []

    for conf_section in hass_config[DOMAIN]:
        if CONF_TRIGGER in conf_section:
            coordinator_tasks.append(init_coordinator(hass, conf_section))
            continue

        for platform_domain in PLATFORMS:
            if platform_domain in conf_section:
                hass.async_create_task(
                    discovery.async_load_platform(
                        hass,
                        platform_domain,
                        DOMAIN,
                        {
                            "unique_id": conf_section.get(CONF_UNIQUE_ID),
                            "entities": conf_section[platform_domain],
                        },
                        hass_config,
                    )
                )

    if coordinator_tasks:
        hass.data[DOMAIN] = await asyncio.gather(*coordinator_tasks)


class TriggerUpdateCoordinator(update_coordinator.DataUpdateCoordinator):
    """Class to handle incoming data."""

    REMOVE_TRIGGER = object()

    def __init__(self, hass, config):
        """Instantiate trigger data."""
        super().__init__(hass, _LOGGER, name="Trigger Update Coordinator")
        self.config = config
        self._unsub_start: Callable[[], None] | None = None
        self._unsub_trigger: Callable[[], None] | None = None
        self._script: Script | None = None

    @property
    def unique_id(self) -> str | None:
        """Return unique ID for the entity."""
        return self.config.get("unique_id")

    @callback
    def async_remove(self):
        """Signal that the entities need to remove themselves."""
        if self._unsub_start:
            self._unsub_start()
        if self._unsub_trigger:
            self._unsub_trigger()

    async def async_setup(self, hass_config: ConfigType) -> None:
        """Set up the trigger and create entities."""
        if self.hass.state == CoreState.running:
            await self._attach_triggers()
        else:
            self._unsub_start = self.hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_START, self._attach_triggers
            )

        for platform_domain in PLATFORMS:
            if platform_domain in self.config:
                self.hass.async_create_task(
                    discovery.async_load_platform(
                        self.hass,
                        platform_domain,
                        DOMAIN,
                        {"coordinator": self, "entities": self.config[platform_domain]},
                        hass_config,
                    )
                )

    async def _attach_triggers(self, start_event=None) -> None:
        """Attach the triggers."""
        if CONF_ACTION in self.config:
            self._script = Script(
                self.hass,
                self.config[CONF_ACTION],
                self.name,
                DOMAIN,
            )

        if start_event is not None:
            self._unsub_start = None

        self._unsub_trigger = await trigger_helper.async_initialize_triggers(
            self.hass,
            self.config[CONF_TRIGGER],
            self._handle_triggered,
            DOMAIN,
            self.name,
            self.logger.log,
            start_event is not None,
        )

    async def _handle_triggered(self, run_variables, context=None):
        if self._script:
            script_result = await self._script.async_run(run_variables, context)
            if script_result:
                run_variables = script_result.variables
        self.async_set_updated_data(
            {"run_variables": run_variables, "context": context}
        )
