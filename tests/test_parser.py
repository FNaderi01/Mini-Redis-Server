"""Tests for parse_inline: raw input line -> list[bytes]."""
import pytest

from main import parse_inline


@pytest.mark.parametrize("line, expected", [
    (b"SET k v", [b"SET", b"k", b"v"]),
    (b"  GET   k  ", [b"GET", b"k"]),
    (b"PING", [b"PING"]),
    (b"", []),
    (b"   ", []),
    (b"SET \xff \x80", [b"SET", b"\xff", b"\x80"]),
])
def test_parse_inline_splits_on_whitespace(line, expected):
    assert(parse_inline(line) == expected)


def test_parse_inline_accepts_bytearray():
    assert(parse_inline(bytearray(b"GET k")) == [b"GET", b"k"])


@pytest.mark.parametrize("line", [None, 123, "GET k"])
def test_parse_inline_rejects_non_bytes(line):
    with pytest.raises(TypeError):
        parse_inline(line)
