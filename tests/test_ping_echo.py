"""Tests for PING and ECHO."""
import pytest


def test_ping_returns_pong(redis):
    pout = redis.process_command("PING")
    assert(pout == b"PONG")


def test_ping_with_args_is_rejected(redis):
    with pytest.raises(ValueError, match="Invalid number of arguments for PING"):
        redis.process_command("PING 4")


def test_echo_returns_message(redis):
    eout = redis.process_command("ECHO Hello World!")
    assert(eout == b"Hello World!")


def test_echo_without_args_is_rejected(redis):
    with pytest.raises(ValueError, match="Invalid number of arguments for ECHO"):
        redis.process_command("ECHO")
