"""Tests for command parsing: unknown commands, case-insensitivity, argument counts."""
import pytest


def test_unknown_command_raises(redis):
    with pytest.raises(ValueError, match="Command not supported"):
        redis.process_command("FOO BAR")


@pytest.mark.parametrize("cmd", ["", "   "])
def test_empty_command_raises(redis, cmd):
    with pytest.raises(ValueError, match="Empty command"):
        redis.process_command(cmd)


@pytest.mark.parametrize("cmd", [None, 123, b"PING"])
def test_non_str_command_raises_type_error(redis, cmd):
    with pytest.raises(TypeError):
        redis.process_command(cmd)


def test_command_name_is_case_insensitive(redis):
    sout = redis.process_command("SET 4 Alice")
    assert(sout == b"OK")
    sout = redis.process_command("set 4 Alice")
    assert(sout == b"OK")
    sout = redis.process_command("sEt 4 Alice")
    assert(sout == b"OK")


@pytest.mark.parametrize("cmd", ["GET", "GET 4 8"])
def test_get_with_wrong_arg_count(redis, cmd):
    with pytest.raises(ValueError, match="Invalid number of arguments for GET"):
        redis.process_command(cmd)


@pytest.mark.parametrize("cmd", ["SET 4", "SET 4 Alice Bob"])
def test_set_with_wrong_arg_count(redis, cmd):
    with pytest.raises(ValueError, match="Invalid number of arguments for SET"):
        redis.process_command(cmd)


@pytest.mark.parametrize("cmd", ["DEL", "DEL 4 Alice"])
def test_del_with_wrong_arg_count(redis, cmd):
    with pytest.raises(ValueError, match="Invalid number of arguments for DEL"):
        redis.process_command(cmd)


@pytest.mark.parametrize("cmd", ["EXISTS", "EXISTS 4 Alice"])
def test_exists_with_wrong_arg_count(redis, cmd):
    with pytest.raises(ValueError, match="Invalid number of arguments for EXISTS"):
        redis.process_command(cmd)


def test_failed_set_does_not_change_store(redis):
    with pytest.raises(ValueError):
        redis.process_command("SET 4 Alice Bob")
    assert(redis.process_command("GET 4") is None)
