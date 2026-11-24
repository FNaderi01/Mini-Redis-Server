"""Tests for GET and SET."""

def test_set_returns_ok(redis):
    sout = redis.process_command("SET 4 Alice")
    assert(sout == b"OK")


def test_get_after_set_returns_value(redis):
    sout = redis.process_command("SET 4 Alice")
    assert(sout == b"OK")
    gout = redis.process_command("GET 4")
    assert(gout == b"Alice")


def test_get_missing_key_returns_none(redis):
    sout = redis.process_command("GET 4")
    assert(sout is None)

def test_set_overwrites_existing_value(redis):
    redis.process_command("SET 4 Alice")
    gout = redis.process_command("GET 4")
    assert(gout == b"Alice")
    sout = redis.process_command("SET 4 Bob")
    assert(sout == b"OK")
    gout = redis.process_command("GET 4")
    assert(gout == b"Bob")
