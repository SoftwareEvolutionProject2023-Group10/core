"""Util functions for testing."""


def assert_none(entity, neg=False):
    """Assert none helper."""
    if neg:
        assert entity is not None
    else:
        assert entity is None
