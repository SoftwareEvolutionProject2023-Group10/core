"""Helpers for the test harness."""
from unittest.mock import patch

from .const import FAKE_UUID, GET_UUID_FUNCTION


def patch_uuid(return_value: str = FAKE_UUID):
    """Ensure that UUIDs aren't requested from the network.

    All returned UUIDs will be return_value (defaulting to FAKE_UUID).
    """
    return patch(GET_UUID_FUNCTION, return_value=return_value)
