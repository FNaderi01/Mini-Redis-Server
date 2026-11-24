"""Tests for command validation: unknown commands, case-insensitivity, argument counts."""
import pytest


def test_unknown_command_raises(redis):
    with pytest.raises(ValueError, match="Command not supported"):
        redis.process_command([b"FOO", b"BAR"])


def test_empty_command_raises(redis):
    with pytest.raises(ValueError, match="Empty command"):
        redis.process_command([])


@pytest.mark.parametrize("args", [None, b"PING", "PING", [b"SET", "k", b"v"], [b"GET", 4]])
def test_non_list_of_bytes_raises_type_error(redis, args):
    with pytest.raises(TypeError):
        redis.process_command(args)


def test_arguments_can_contain_spaces(redis):
    sout = redis.process_command([b"SET", b"name", b"John Smith"])
    assert(sout == b"OK")
    gout = redis.process_command([b"GET", b"name"])
    assert(gout == b"John Smith")


def test_non_utf8_key_and_value(redis):
    sout = redis.process_command([b"SET", b"\xff\xfe", b"\x80\x81"])
    assert(sout == b"OK")
    gout = redis.process_command([b"GET", b"\xff\xfe"])
    assert(gout == b"\x80\x81")


def test_command_name_is_case_insensitive(redis):
    sout = redis.process_command([b"SET", b"4", b"Alice"])
    assert(sout == b"OK")
    sout = redis.process_command([b"set", b"4", b"Alice"])
    assert(sout == b"OK")
    sout = redis.process_command([b"sEt", b"4", b"Alice"])
    assert(sout == b"OK")


def test_caller_list_is_not_modified(redis):
    args = [b"SET", b"4", b"Alice"]
    redis.process_command(args)
    assert(args == [b"SET", b"4", b"Alice"])


@pytest.mark.parametrize("args", [[b"GET"], [b"GET", b"4", b"8"]])
def test_get_with_wrong_arg_count(redis, args):
    with pytest.raises(ValueError, match="Invalid number of arguments for GET"):
        redis.process_command(args)


@pytest.mark.parametrize("args", [[b"SET", b"4"], [b"SET", b"4", b"Alice", b"Bob"]])
def test_set_with_wrong_arg_count(redis, args):
    with pytest.raises(ValueError, match="Invalid number of arguments for SET"):
        redis.process_command(args)


@pytest.mark.parametrize("args", [[b"DEL"], [b"DEL", b"4", b"Alice"]])
def test_del_with_wrong_arg_count(redis, args):
    with pytest.raises(ValueError, match="Invalid number of arguments for DEL"):
        redis.process_command(args)


@pytest.mark.parametrize("args", [[b"EXISTS"], [b"EXISTS", b"4", b"Alice"]])
def test_exists_with_wrong_arg_count(redis, args):
    with pytest.raises(ValueError, match="Invalid number of arguments for EXISTS"):
        redis.process_command(args)


def test_failed_set_does_not_change_store(redis):
    with pytest.raises(ValueError):
        redis.process_command([b"SET", b"4", b"Alice", b"Bob"])
    assert(redis.process_command([b"GET", b"4"]) is None)
