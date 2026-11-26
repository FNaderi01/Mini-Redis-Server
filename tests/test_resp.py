"""Tests for resp.py: parsing RESP requests and serializing replies."""
import pytest

from main import CMD, MiniRedis
from resp import IncompleteRequest, MiniRESP, ProtocolError

CRLF = b"\r\n"


@pytest.fixture
def resp():
    return MiniRESP()


def encode(args: list[bytes]) -> bytes:
    """Build a RESP request the way a client would (independent of MiniRESP)."""
    out = b"*" + str(len(args)).encode() + CRLF
    for arg in args:
        out += b"$" + str(len(arg)).encode() + CRLF + arg + CRLF
    return out


# --------------------------------------------------------------------------
# Exception types
# --------------------------------------------------------------------------

def test_protocol_error_is_a_value_error():
    # so a generic `except ValueError` in the server loop also catches it
    assert issubclass(ProtocolError, ValueError)


def test_incomplete_request_is_not_a_value_error():
    # "need more bytes" must never be swallowed by `except ValueError`
    assert not issubclass(IncompleteRequest, ValueError)


# --------------------------------------------------------------------------
# parser: valid input
# --------------------------------------------------------------------------

@pytest.mark.parametrize("data, expected", [
    (b"*1\r\n$4\r\nPING\r\n", [b"PING"]),
    (b"*2\r\n$3\r\nGET\r\n$4\r\nname\r\n", [b"GET", b"name"]),
    (b"*3\r\n$3\r\nSET\r\n$1\r\nk\r\n$1\r\nv\r\n", [b"SET", b"k", b"v"]),
    (b"*3\r\n$3\r\nSET\r\n$1\r\nk\r\n$0\r\n\r\n", [b"SET", b"k", b""]),                 # empty value
    (b"*2\r\n$4\r\nECHO\r\n$4\r\nA\r\nB\r\n", [b"ECHO", b"A\r\nB"]),                     # CRLF inside data
    (b"*2\r\n$4\r\nECHO\r\n$3\r\n\x00\xff$\r\n", [b"ECHO", b"\x00\xff$"]),               # binary data
    (b"*3\r\n$3\r\nSET\r\n$4\r\nname\r\n$10\r\njohn smith\r\n",
     [b"SET", b"name", b"john smith"]),                                                  # spaces, 2-digit length
    (b"*0\r\n", []),                                                                     # empty array
], ids=["ping", "get", "set", "empty-value", "crlf-in-data", "binary", "spaces", "empty-array"])
def test_parser_valid(resp, data, expected):
    args, consumed = resp.parser(data)
    assert args == expected
    assert consumed == len(data)


@pytest.mark.parametrize("args", [
    [b"PING"],
    [b"SET", b"k", b"\r\n"],
    [b"SET", b"*1\r\n", b"$3\r\n"],     # data that looks like RESP headers
    [b"ECHO", bytes(range(256))],       # every possible byte value
    [b"ECHO", b"x" * 10_000],           # long value, 5-digit length
])
def test_parser_round_trip(resp, args):
    assert resp.parser(encode(args)) == (args, len(encode(args)))


def test_parser_does_not_lowercase_or_modify_args(resp):
    args, _ = resp.parser(encode([b"SeT", b"Key", b"VALUE"]))
    assert args == [b"SeT", b"Key", b"VALUE"]


# --------------------------------------------------------------------------
# parser: incomplete input (valid so far, wait for more bytes)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("data", [
    b"",                              # empty buffer
    b"*",                             # array prefix only
    b"*2",                            # header without CRLF
    b"*2\r",                          # half a CRLF
    b"*2\r\n",                        # header done, no elements yet
    b"*2\r\n$3\r\nGET\r\n",           # first element done, second missing
    b"*1\r\n$",                       # bulk prefix only
    b"*1\r\n$4",                      # bulk header without CRLF
    b"*1\r\n$4\r\n",                  # bulk header done, no data
    b"*1\r\n$4\r\nPI",                # partial data
    b"*1\r\n$4\r\nPING",              # data done, no CRLF
    b"*1\r\n$4\r\nPING\r",            # data done, half a CRLF
])
def test_parser_incomplete(resp, data):
    with pytest.raises(IncompleteRequest):
        resp.parser(data)


@pytest.mark.parametrize("args", [
    [b"PING"],
    [b"SET", b"name", b"john smith"],
    [b"ECHO", b"A\r\nB"],
    [b"SET", b"k", b""],
])
def test_every_prefix_of_a_valid_request_is_incomplete(resp, args):
    """Simulates TCP delivering a request one byte at a time."""
    data = encode(args)
    for cut in range(len(data)):
        with pytest.raises(IncompleteRequest):
            resp.parser(data[:cut])
    assert resp.parser(data) == (args, len(data))


# --------------------------------------------------------------------------
# parser: malformed input
# --------------------------------------------------------------------------

@pytest.mark.parametrize("data, message", [
    (b"+OK\r\n", "Expected"),                                   # not an array
    (b"PING\r\n", "Expected"),                                  # inline command, not RESP
    (b"*abc\r\n", "Invalid Array length"),
    (b"*-1\r\n", "Invalid Array length"),                       # null array isn't a valid request
    (b"*\r\n", "Invalid Array length"),                         # missing number
    (b"*1\r\n:5\r\n", "Expected Bulk string"),                  # integer instead of bulk string
    (b"*1\r\n+PING\r\n", "Expected Bulk string"),               # simple string instead of bulk string
    (b"*1\r\n$abc\r\nPING\r\n", "Invalid Bulk string length"),
    (b"*1\r\n$-1\r\n", "Invalid Bulk string length"),           # null bulk string isn't a valid argument
    (b"*1\r\n$\r\n", "Invalid Bulk string length"),
    (b"*1\r\n$4\r\nPINGXX", "Invalid CRLF"),                    # wrong terminator
    (b"*1\r\n$4\r\nPINGX", "Invalid CRLF"),                     # wrong first terminator byte
    (b"*1\r\n$4\r\nPING\rX", "Invalid CRLF"),                   # wrong second terminator byte
    (b"*1\r\n$4\r\nPING\n\r", "Invalid CRLF"),                  # reversed terminator
    (b"*1\r\n$3\r\nPING\r\n", "Invalid CRLF"),                  # length shorter than data
    (b"*2\r\n$1\r\nkXX$1\r\nv\r\n", "Invalid CRLF"),            # junk between elements
], ids=lambda v: v if isinstance(v, str) else None)
def test_parser_protocol_error(resp, data, message):
    with pytest.raises(ProtocolError, match=message):
        resp.parser(data)


# --------------------------------------------------------------------------
# parser: the idx parameter / several commands in one buffer
# --------------------------------------------------------------------------

def test_parser_two_pipelined_commands(resp):
    first, second = [b"SET", b"k", b"v"], [b"GET", b"k"]
    data = encode(first) + encode(second)

    args, idx = resp.parser(data)
    assert args == first
    assert idx == len(encode(first))

    args, idx = resp.parser(data, idx)
    assert args == second
    assert idx == len(data)


def test_parser_idx_at_end_of_buffer_is_incomplete(resp):
    data = encode([b"PING"])
    with pytest.raises(IncompleteRequest):
        resp.parser(data, len(data))


def test_parser_complete_command_followed_by_partial_one(resp):
    data = encode([b"PING"]) + b"*2\r\n$3\r\nGET"
    args, idx = resp.parser(data)
    assert args == [b"PING"]
    with pytest.raises(IncompleteRequest):
        resp.parser(data, idx)


def test_parser_complete_command_followed_by_garbage(resp):
    data = encode([b"PING"]) + b"garbage\r\n"
    args, idx = resp.parser(data)
    assert args == [b"PING"]
    with pytest.raises(ProtocolError):
        resp.parser(data, idx)


def test_parser_empty_array_then_command(resp):
    data = b"*0\r\n" + encode([b"PING"])
    args, idx = resp.parser(data)
    assert (args, idx) == ([], 4)
    assert resp.parser(data, idx) == ([b"PING"], len(data))


def test_parser_empty_array_then_garbage(resp):
    data = b"*0\r\n$3\r\nGET\r\n"
    args, idx = resp.parser(data)
    assert args == []
    with pytest.raises(ProtocolError):
        resp.parser(data, idx)


# --------------------------------------------------------------------------
# serialize: valid results
# --------------------------------------------------------------------------

@pytest.mark.parametrize("cmd_type, result, expected", [
    (CMD.GET, b"Alice", b"$5\r\nAlice\r\n"),
    (CMD.GET, b"", b"$0\r\n\r\n"),                       # empty value is not the same as missing
    (CMD.GET, None, b"$-1\r\n"),                         # missing key -> null bulk string
    (CMD.GET, b"a\r\nb", b"$4\r\na\r\nb\r\n"),           # CRLF inside value is length-prefixed
    (CMD.GET, b"0123456789", b"$10\r\n0123456789\r\n"),  # 2-digit length
    (CMD.SET, b"OK", b"+OK\r\n"),
    (CMD.DEL, 0, b":0\r\n"),
    (CMD.DEL, 1, b":1\r\n"),
    (CMD.EXISTS, 0, b":0\r\n"),
    (CMD.EXISTS, 1, b":1\r\n"),
    (CMD.PING, b"PONG", b"+PONG\r\n"),
    (CMD.ECHO, b"hi", b"$2\r\nhi\r\n"),
    (CMD.ECHO, b"", b"$0\r\n\r\n"),
    (CMD.ECHO, b"\x00\xff", b"$2\r\n\x00\xff\r\n"),
])
def test_serialize_valid(resp, cmd_type, result, expected):
    assert resp.serialize(cmd_type, result) == expected


# --------------------------------------------------------------------------
# serialize: results that don't match the command type
# --------------------------------------------------------------------------

@pytest.mark.parametrize("cmd_type, result", [
    (CMD.GET, 5),
    (CMD.GET, "Alice"),               # str, not bytes
    (CMD.GET, bytearray(b"Alice")),   # only exact bytes is accepted
    (CMD.SET, b"NOPE"),
    (CMD.SET, "OK"),
    (CMD.SET, None),
    (CMD.DEL, 2),
    (CMD.DEL, -1),
    (CMD.DEL, b"1"),
    (CMD.DEL, True),                  # bool is not accepted as int
    (CMD.EXISTS, None),
    (CMD.PING, b"PING"),
    (CMD.PING, None),
    (CMD.ECHO, None),
    (CMD.ECHO, "hi"),
    (None, b"x"),                     # not a CMD at all
    ("GET", b"x"),
])
def test_serialize_invalid_result_returns_error(resp, cmd_type, result):
    out = resp.serialize(cmd_type, result)
    assert out.startswith(b"-ERR ")
    assert out.endswith(CRLF)
    assert out.count(CRLF) == 1       # a RESP error must be a single line


# --------------------------------------------------------------------------
# End to end: bytes in -> MiniRedis -> bytes out
# --------------------------------------------------------------------------

def test_end_to_end_session(resp):
    """A whole session sent in one buffer, parsed, run and serialized command by command."""
    redis = MiniRedis()
    session = [
        ([b"PING"],                          b"+PONG\r\n"),
        ([b"ECHO", b"hello world"],          b"$11\r\nhello world\r\n"),
        ([b"GET", b"name"],                  b"$-1\r\n"),
        ([b"EXISTS", b"name"],               b":0\r\n"),
        ([b"SET", b"name", b"john smith"],   b"+OK\r\n"),
        ([b"GET", b"name"],                  b"$10\r\njohn smith\r\n"),
        ([b"EXISTS", b"name"],               b":1\r\n"),
        ([b"DEL", b"name"],                  b":1\r\n"),
        ([b"DEL", b"name"],                  b":0\r\n"),
        ([b"GET", b"name"],                  b"$-1\r\n"),
    ]
    data = b"".join(encode(request) for request, _ in session)

    replies, idx = [], 0
    while idx < len(data):
        args, idx = resp.parser(data, idx)
        replies.append(resp.serialize(*redis.process_command(args)))

    assert replies == [reply for _, reply in session]
