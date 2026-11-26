"""Tests for DEL and EXISTS."""
from main import CMD


def test_del_existing_key_returns_1(redis):
    redis.process_command([b"SET", b"4", b"Alice"])
    assert(redis.process_command([b"DEL", b"4"]) == (CMD.DEL, 1))


def test_del_missing_key_returns_0(redis):
    assert(redis.process_command([b"DEL", b"4"]) == (CMD.DEL, 0))


def test_get_after_del_returns_none(redis):
    redis.process_command([b"SET", b"4", b"Alice"])
    assert(redis.process_command([b"GET", b"4"]) == (CMD.GET, b"Alice"))
    assert(redis.process_command([b"DEL", b"4"]) == (CMD.DEL, 1))
    assert(redis.process_command([b"GET", b"4"]) == (CMD.GET, None))


def test_exists_returns_1_for_existing_key(redis):
    redis.process_command([b"SET", b"4", b"Alice"])
    assert(redis.process_command([b"EXISTS", b"4"]) == (CMD.EXISTS, 1))


def test_exists_returns_0_for_missing_key(redis):
    assert(redis.process_command([b"EXISTS", b"4"]) == (CMD.EXISTS, 0))
