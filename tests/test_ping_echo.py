"""Tests for PING and ECHO."""
import pytest


def test_ping_returns_pong(redis):
    pout = redis.process_command([b"PING"])
    assert(pout == b"PONG")


def test_ping_with_args_is_rejected(redis):
    with pytest.raises(ValueError, match="Invalid number of arguments for PING"):
        redis.process_command([b"PING", b"4"])


def test_echo_returns_message(redis):
    eout = redis.process_command([b"ECHO", b"Hello World!"])
    assert(eout == b"Hello World!")


@pytest.mark.parametrize("args", [[b"ECHO"], [b"ECHO", b"Hello", b"World!"]])
def test_echo_with_wrong_arg_count_is_rejected(redis, args):
    with pytest.raises(ValueError, match="Invalid number of arguments for ECHO"):
        redis.process_command(args)
