"""Tests for command parsing: unknown commands, case-insensitivity, argument counts."""


def test_unknown_command_returns_none(redis, capsys):
    out = redis.process_command("FOO BAR")
    assert(out is None)


def test_command_name_is_case_insensitive(redis):
    sout = redis.process_command("SET 4 Alice")
    assert(sout == b"OK")
    sout = redis.process_command("set 4 Alice")
    assert(sout == b"OK")
    sout = redis.process_command("sEt 4 Alice")
    assert(sout == b"OK")

def test_get_with_wrong_arg_count(redis, capsys):
    sout = redis.process_command("GET 4 8")
    assert(sout is None)
    sout = redis.process_command("GET")
    assert(sout is None)


def test_set_with_wrong_arg_count(redis, capsys):
    sout = redis.process_command("SET 4")
    assert(sout is None)
    sout = redis.process_command("SET 4 Alice Bob")
    assert(sout is None)


def test_del_with_wrong_arg_count(redis, capsys):
    dout = redis.process_command("DEL")
    assert(dout is None)
    dout = redis.process_command("DEL 4 Alice")
    assert(dout is None)


def test_exists_with_wrong_arg_count(redis, capsys):
    eout = redis.process_command("EXISTS")
    assert(eout is None)
    eout = redis.process_command("EXISTS 4 Alice")
    assert(eout is None)
