"""Util functions for testing."""


def assert_none(entity, neg=False):
    """Assert none helper."""
    if neg:
        assert entity is not None
    else:
        assert entity is None


def assert_length(checker, length):
    """Assert the length of a sequence.

    Example:
        Assert that the length of `checker` is equal to `length`.
    """
    assert len(checker) == length
