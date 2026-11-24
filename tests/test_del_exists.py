"""Tests for DEL and EXISTS."""


def test_del_existing_key_returns_1(redis):
    redis.process_command("SET 4 Alice")
    dout = redis.process_command("DEL 4")
    assert(dout == 1)


def test_del_missing_key_returns_0(redis):
    dout = redis.process_command("DEL 4")
    assert(dout == 0)


def test_get_after_del_returns_none(redis):
    redis.process_command("SET 4 Alice")
    gout = redis.process_command("GET 4")
    assert(gout == b"Alice")
    sout = redis.process_command("DEL 4")
    assert(sout == 1)
    gout = redis.process_command("GET 4")
    assert(gout is None)
    

def test_exists_returns_1_for_existing_key(redis):
    redis.process_command("SET 4 Alice")
    eout = redis.process_command("EXISTS 4")
    assert(eout == 1)


def test_exists_returns_0_for_missing_key(redis):
    eout = redis.process_command("EXISTS 4")
    assert(eout == 0)
