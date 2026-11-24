"""Tests for command parsing: unknown commands, case-insensitivity, argument counts."""


def test_unknown_command_returns_none(redis, capsys):
    # TODO: process "FOO bar", assert result is None and "Command not supported" was printed
    pass


def test_command_name_is_case_insensitive(redis):
    # TODO: "SET k v", "set k v" and "SeT k v" should all behave the same
    pass


def test_get_with_wrong_arg_count(redis, capsys):
    # TODO: "GET" and "GET a b" should return None and print an error
    pass


def test_set_with_wrong_arg_count(redis, capsys):
    # TODO: "SET k" and "SET k v extra" should return None and print an error
    pass


def test_del_with_wrong_arg_count(redis, capsys):
    # TODO
    pass


def test_exists_with_wrong_arg_count(redis, capsys):
    # TODO
    pass
