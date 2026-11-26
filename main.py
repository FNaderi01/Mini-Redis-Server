import sys
from enum import Enum
class CMD(Enum):
    GET = 1
    SET = 2
    DEL = 3
    EXISTS = 4
    PING = 5
    ECHO = 6


def parse_inline(line: bytes) -> list[bytes]:
    """Turn one raw input line into a list of arguments, e.g. b"SET k v" -> [b"SET", b"k", b"v"].

    This is the only place that knows about the input format. Later it can be
    swapped for a RESP parser without touching MiniRedis.
    """
    if not isinstance(line, (bytes, bytearray, memoryview)):
        raise TypeError(f"Input line must be bytes, not {type(line).__name__}.")
    return bytes(line).split()


class MiniRedis:
    
    def __init__(self):
        self.store  : dict[bytes, bytes] = {}
        self.supported_commands = {
            b'get' : CMD.GET,
            b'set' : CMD.SET,
            b'del' : CMD.DEL,
            b'ping' : CMD.PING,
            b'echo' : CMD.ECHO,
            b'exists' : CMD.EXISTS
        }

    @staticmethod
    def _check_arg_count(args: list[bytes], name: str, expected: int) -> None:
        """Raise ValueError unless the command has exactly `expected` arguments."""
        if len(args) - 1 != expected:
            raise ValueError(
                f"Invalid number of arguments for {name}: "
                f"expected {expected}, got {len(args) - 1}."
            )

    def process_command(self, args : list[bytes]) -> tuple[CMD, bytes | int | None]:
        """Run one command and return (command_type, result).

        Raises TypeError for badly-typed input and ValueError for invalid commands.
        """
        if not isinstance(args, (list, tuple)):
            raise TypeError(f"Command must be a list of bytes, not {type(args).__name__}.")
        for arg in args:
            if not isinstance(arg, bytes):
                raise TypeError(f"Every argument must be bytes, got {type(arg).__name__}.")
        if not args:
            raise ValueError("Empty command.")

        name = args[0].lower()  # don't modify the caller's list
        if name not in self.supported_commands:
            raise ValueError(f"Command not supported: {name!r}.")
        
        cmd_type = self.supported_commands[name]
        result : bytes | int | None
        match cmd_type:
            case CMD.GET:
                self._check_arg_count(args, "GET", 1)
                result = self.store.get(args[1])
            case CMD.SET:
                self._check_arg_count(args, "SET", 2)
                self.store[args[1]] = args[2]
                result = b"OK"
            case CMD.DEL:
                self._check_arg_count(args, "DEL", 1)
                result = 1 if self.store.pop(args[1], None) is not None else 0
            case CMD.PING:
                self._check_arg_count(args, "PING", 0)
                result = b"PONG"
            case CMD.ECHO:
                self._check_arg_count(args, "ECHO", 1)
                result = args[1]
            case CMD.EXISTS:
                self._check_arg_count(args, "EXISTS", 1)
                result = 1 if args[1] in self.store else 0
        return cmd_type, result



if __name__ == "__main__":
    stdin = sys.stdin.buffer  # read raw bytes instead of decoded str
    n = int(stdin.readline())
    my_redis = MiniRedis()
    for i in range(n) :
        line = stdin.readline().rstrip(b"\r\n")
        try:
            cmd_type, result = my_redis.process_command(parse_inline(line))
            print(result)
        except ValueError as e:
            print(f"ERR {e}")
