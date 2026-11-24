"""Tests for DEL and EXISTS."""


def test_del_existing_key_returns_1(redis):
    redis.process_command([b"SET", b"4", b"Alice"])
    dout = redis.process_command([b"DEL", b"4"])
    assert(dout == 1)


def test_del_missing_key_returns_0(redis):
    dout = redis.process_command([b"DEL", b"4"])
    assert(dout == 0)


def test_get_after_del_returns_none(redis):
    redis.process_command([b"SET", b"4", b"Alice"])
    gout = redis.process_command([b"GET", b"4"])
    assert(gout == b"Alice")
    sout = redis.process_command([b"DEL", b"4"])
    assert(sout == 1)
    gout = redis.process_command([b"GET", b"4"])
    assert(gout is None)
    

def test_exists_returns_1_for_existing_key(redis):
    redis.process_command([b"SET", b"4", b"Alice"])
    eout = redis.process_command([b"EXISTS", b"4"])
    assert(eout == 1)


def test_exists_returns_0_for_missing_key(redis):
    eout = redis.process_command([b"EXISTS", b"4"])
    assert(eout == 0)
