"""Tests for GET and SET."""
from main import CMD, MiniRedis


def test_set_returns_ok(redis):
    assert(redis.process_command([b"SET", b"4", b"Alice"]) == (CMD.SET, b"OK"))


def test_get_after_set_returns_value(redis):
    assert(redis.process_command([b"SET", b"4", b"Alice"]) == (CMD.SET, b"OK"))
    assert(redis.process_command([b"GET", b"4"]) == (CMD.GET, b"Alice"))


def test_get_missing_key_returns_none(redis):
    assert(redis.process_command([b"GET", b"4"]) == (CMD.GET, None))


def test_set_overwrites_existing_value(redis):
    redis.process_command([b"SET", b"4", b"Alice"])
    assert(redis.process_command([b"GET", b"4"]) == (CMD.GET, b"Alice"))
    assert(redis.process_command([b"SET", b"4", b"Bob"]) == (CMD.SET, b"OK"))
    assert(redis.process_command([b"GET", b"4"]) == (CMD.GET, b"Bob"))


def test_empty_value_round_trip(redis):
    # b"" is falsy like None, so make sure it's stored and returned, not treated as missing.
    # (CMD.GET, b"") != (CMD.GET, None), so the tuple comparison catches that.
    assert(redis.process_command([b"SET", b"k", b""]) == (CMD.SET, b"OK"))
    assert(redis.process_command([b"GET", b"k"]) == (CMD.GET, b""))
    assert(redis.process_command([b"EXISTS", b"k"]) == (CMD.EXISTS, 1))
    assert(redis.process_command([b"DEL", b"k"]) == (CMD.DEL, 1))


def test_instances_are_independent():
    # guards against `store` accidentally becoming a shared class attribute
    a, b = MiniRedis(), MiniRedis()
    a.process_command([b"SET", b"k", b"1"])
    assert(b.process_command([b"GET", b"k"]) == (CMD.GET, None))
    assert(b.process_command([b"EXISTS", b"k"]) == (CMD.EXISTS, 0))
    b.process_command([b"SET", b"k", b"2"])
    assert(a.process_command([b"GET", b"k"]) == (CMD.GET, b"1"))
