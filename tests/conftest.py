import pytest

from main import MiniRedis


@pytest.fixture
def redis():
    """A fresh MiniRedis instance for every test (empty store)."""
    return MiniRedis()
