"""Philips Hue scene platform tests for V2 bridge/api."""
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er

from .conftest import setup_platform
from .const import FAKE_SCENE
from .utils import assert_none


async def assert_scene_attributes(
    test_entity: State, name, state, group_name, group_type, scene_name, attributes
):
    """Assert method for assert scenes."""
    assert_none(test_entity, True)
    assert test_entity.name == name
    assert test_entity.state == state
    assert test_entity.attributes["group_name"] == group_name
    assert test_entity.attributes["group_type"] == group_type
    assert test_entity.attributes["name"] == scene_name
    for key, value in attributes.items():
        assert test_entity.attributes[key] == value


async def test_scene(
    hass: HomeAssistant, mock_bridge_v2, v2_resources_test_data
) -> None:
    """Test if (config) scenes get created."""
    await mock_bridge_v2.api.load_test_data(v2_resources_test_data)

    await setup_platform(hass, mock_bridge_v2, "scene")
    # there shouldn't have been any requests at this point
    assert len(mock_bridge_v2.mock_requests) == 0
    # 3 entities should be created from test data
    assert len(hass.states.async_all()) == 3

    # test (dynamic) scene for a hue zone
    await assert_scene_attributes(
        hass.states.get("scene.test_zone_dynamic_test_scene"),
        "Test Zone Dynamic Test Scene",
        STATE_UNKNOWN,
        "Test Zone",
        "zone",
        "Dynamic Test Scene",
        {
            "speed": 0.6269841194152832,
            "brightness": 46.85,
            "is_dynamic": True,
        },
    )

    # test (regular) scene for a hue room
    await assert_scene_attributes(
        hass.states.get("scene.test_room_regular_test_scene"),
        "Test Room Regular Test Scene",
        STATE_UNKNOWN,
        "Test Room",
        "room",
        "Regular Test Scene",
        {
            "speed": 0.5,
            "brightness": 100.0,
            "is_dynamic": False,
        },
    )

    # test smart scene
    await assert_scene_attributes(
        hass.states.get("scene.test_room_smart_test_scene"),
        "Test Room Smart Test Scene",
        STATE_UNKNOWN,
        "Test Room",
        "room",
        "Smart Test Scene",
        {
            "active_timeslot_id": 1,
            "active_timeslot_name": "wednesday",
            "active_scene": "Regular Test Scene",
            "is_active": True,
        },
    )

    # scene entities should have be assigned to the room/zone device/service
    ent_reg = er.async_get(hass)
    for entity_id in (
        "scene.test_zone_dynamic_test_scene",
        "scene.test_room_regular_test_scene",
        "scene.test_room_smart_test_scene",
    ):
        entity_entry = ent_reg.async_get(entity_id)
        assert entity_entry
        assert entity_entry.device_id is not None


async def test_scene_turn_on_service(
    hass: HomeAssistant, mock_bridge_v2, v2_resources_test_data
) -> None:
    """Test calling the turn on service on a scene."""
    await mock_bridge_v2.api.load_test_data(v2_resources_test_data)

    await setup_platform(hass, mock_bridge_v2, "scene")

    test_entity_id = "scene.test_room_regular_test_scene"

    # call the HA turn_on service
    await hass.services.async_call(
        "scene",
        "turn_on",
        {"entity_id": test_entity_id},
        blocking=True,
    )

    # PUT request should have been sent to device with correct params
    assert len(mock_bridge_v2.mock_requests) == 1
    assert mock_bridge_v2.mock_requests[0]["method"] == "put"
    assert mock_bridge_v2.mock_requests[0]["json"]["recall"] == {"action": "active"}

    # test again with sending transition
    await hass.services.async_call(
        "scene",
        "turn_on",
        {"entity_id": test_entity_id, "transition": 0.25},
        blocking=True,
    )
    assert len(mock_bridge_v2.mock_requests) == 2
    assert mock_bridge_v2.mock_requests[1]["json"]["recall"] == {
        "action": "active",
        "duration": 200,
    }


async def test_scene_advanced_turn_on_service(
    hass: HomeAssistant, mock_bridge_v2, v2_resources_test_data
) -> None:
    """Test calling the advanced turn on service on a scene."""
    await mock_bridge_v2.api.load_test_data(v2_resources_test_data)

    await setup_platform(hass, mock_bridge_v2, "scene")

    test_entity_id = "scene.test_room_regular_test_scene"

    # call the hue.activate_scene service
    await hass.services.async_call(
        "hue",
        "activate_scene",
        {"entity_id": test_entity_id},
        blocking=True,
    )

    # PUT request should have been sent to device with correct params
    assert len(mock_bridge_v2.mock_requests) == 1
    assert mock_bridge_v2.mock_requests[0]["method"] == "put"
    assert mock_bridge_v2.mock_requests[0]["json"]["recall"] == {"action": "active"}

    # test again with sending speed and dynamic
    await hass.services.async_call(
        "hue",
        "activate_scene",
        {"entity_id": test_entity_id, "speed": 80, "dynamic": True},
        blocking=True,
    )
    assert len(mock_bridge_v2.mock_requests) == 3
    assert mock_bridge_v2.mock_requests[1]["json"]["speed"] == 0.8
    assert mock_bridge_v2.mock_requests[2]["json"]["recall"] == {
        "action": "dynamic_palette",
    }


async def create_fake_scene(hass, mock_bridge_v2, scene_id):
    """Create a fake scene and wait for it to be available."""
    mock_bridge_v2.api.emit_event("add", FAKE_SCENE)
    await hass.async_block_till_done()
    return hass.states.get(scene_id)


async def assert_scene_state(test_entity, name, state, brightness):
    """Assert common scene attributes."""
    assert_none(test_entity, True)
    assert test_entity.state == state
    assert test_entity.name == name
    assert test_entity.attributes["brightness"] == brightness


async def test_scene_updates(
    hass: HomeAssistant, mock_bridge_v2, v2_resources_test_data
) -> None:
    """Test scene events from bridge."""
    await mock_bridge_v2.api.load_test_data(v2_resources_test_data)

    await setup_platform(hass, mock_bridge_v2, "scene")

    test_entity_id = "scene.test_room_mocked_scene"

    # Verify entity does not exist before we start
    assert hass.states.get(test_entity_id) is None

    # Create a fake scene
    test_entity = await create_fake_scene(hass, mock_bridge_v2, test_entity_id)
    await assert_scene_state(test_entity, "Test Room Mocked Scene", STATE_UNKNOWN, 65.0)

    # Test scene update
    updated_resource = {**FAKE_SCENE}
    updated_resource["actions"][0]["action"]["dimming"]["brightness"] = 35.0
    mock_bridge_v2.api.emit_event("update", updated_resource)
    await hass.async_block_till_done()

    # Update the test_entity with the latest state
    test_entity = hass.states.get(test_entity_id)

    await assert_scene_state(test_entity, "Test Room Mocked Scene", STATE_UNKNOWN, 35.0)

    # Test entity name change on group name change
    mock_bridge_v2.api.emit_event(
        "update",
        {
            "type": "room",
            "id": "6ddc9066-7e7d-4a03-a773-c73937968296",
            "metadata": {"name": "Test Room 2"},
        },
    )
    await hass.async_block_till_done()

    # Update the test_entity with the latest state
    test_entity = hass.states.get(test_entity_id)

    await assert_scene_state(
        test_entity, "Test Room 2 Mocked Scene", STATE_UNKNOWN, 35.0
    )

    # Test scene deletion
    mock_bridge_v2.api.emit_event("delete", updated_resource)
    await hass.async_block_till_done()
    assert_none(hass.states.get(test_entity_id), True)
