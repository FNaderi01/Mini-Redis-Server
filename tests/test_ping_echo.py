"""Tests for PING and ECHO."""
import pytest

from main import CMD


def test_ping_returns_pong(redis):
    assert(redis.process_command([b"PING"]) == (CMD.PING, b"PONG"))


def test_ping_with_args_is_rejected(redis):
    with pytest.raises(ValueError, match="Invalid number of arguments for PING"):
        redis.process_command([b"PING", b"4"])


def test_echo_returns_message(redis):
    assert(redis.process_command([b"ECHO", b"Hello World!"]) == (CMD.ECHO, b"Hello World!"))


@pytest.mark.parametrize("args", [[b"ECHO"], [b"ECHO", b"Hello", b"World!"]])
def test_echo_with_wrong_arg_count_is_rejected(redis, args):
    with pytest.raises(ValueError, match="Invalid number of arguments for ECHO"):
        redis.process_command(args)
