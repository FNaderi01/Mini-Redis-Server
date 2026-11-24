"""Tests for PING and ECHO (these print instead of returning, so use capsys)."""


def test_ping_prints_pong(redis, capsys):
    # TODO: process "PING", then check capsys.readouterr().out contains "PONG"
    pass


def test_ping_with_args_is_rejected(redis, capsys):
    # TODO
    pass


def test_echo_prints_message(redis, capsys):
    # TODO: decide what "ECHO hello" should print ("hello" vs the whole command)
    pass


def test_echo_without_args_is_rejected(redis, capsys):
    # TODO
    pass
