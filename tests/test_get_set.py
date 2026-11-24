"""Tests for GET and SET."""
from main import MiniRedis


def test_set_returns_ok(redis):
    sout = redis.process_command([b"SET", b"4", b"Alice"])
    assert(sout == b"OK")


def test_get_after_set_returns_value(redis):
    sout = redis.process_command([b"SET", b"4", b"Alice"])
    assert(sout == b"OK")
    gout = redis.process_command([b"GET", b"4"])
    assert(gout == b"Alice")


def test_get_missing_key_returns_none(redis):
    sout = redis.process_command([b"GET", b"4"])
    assert(sout is None)

def test_set_overwrites_existing_value(redis):
    redis.process_command([b"SET", b"4", b"Alice"])
    gout = redis.process_command([b"GET", b"4"])
    assert(gout == b"Alice")
    sout = redis.process_command([b"SET", b"4", b"Bob"])
    assert(sout == b"OK")
    gout = redis.process_command([b"GET", b"4"])
    assert(gout == b"Bob")


def test_empty_value_round_trip(redis):
    # b"" is falsy like None, so make sure it's stored and returned, not treated as missing
    assert(redis.process_command([b"SET", b"k", b""]) == b"OK")
    result = redis.process_command([b"GET", b"k"])
    assert(result == b"")
    assert(result is not None)
    assert(redis.process_command([b"EXISTS", b"k"]) == 1)
    assert(redis.process_command([b"DEL", b"k"]) == 1)


def test_instances_are_independent():
    # guards against `store` accidentally becoming a shared class attribute
    a, b = MiniRedis(), MiniRedis()
    a.process_command([b"SET", b"k", b"1"])
    assert(b.process_command([b"GET", b"k"]) is None)
    assert(b.process_command([b"EXISTS", b"k"]) == 0)
    b.process_command([b"SET", b"k", b"2"])
    assert(a.process_command([b"GET", b"k"]) == b"1")
