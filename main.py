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

    def process_command(self, args : list[bytes]):
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
        match cmd_type:
            case CMD.GET:
                self._check_arg_count(args, "GET", 1)
                return self.store.get(args[1])
            case CMD.SET:
                self._check_arg_count(args, "SET", 2)
                self.store[args[1]] = args[2]
                return b"OK"
            case CMD.DEL:
                self._check_arg_count(args, "DEL", 1)
                key = args[1]
                if key not in self.store:
                    return 0
                del self.store[key]
                return 1
            case CMD.PING:
                self._check_arg_count(args, "PING", 0)
                return b"PONG"
            case CMD.ECHO:
                self._check_arg_count(args, "ECHO", 1)
                return args[1]
            case CMD.EXISTS:
                self._check_arg_count(args, "EXISTS", 1)
                return 1 if args[1] in self.store else 0



if __name__ == "__main__":
    stdin = sys.stdin.buffer  # read raw bytes instead of decoded str
    n = int(stdin.readline())
    my_reddis = MiniRedis()
    for i in range(n) :
        line = stdin.readline().rstrip(b"\r\n")
        try:
            print(my_reddis.process_command(parse_inline(line)))
        except ValueError as e:
            print(f"ERR {e}")
