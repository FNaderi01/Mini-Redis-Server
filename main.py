from enum import Enum
class CMD(Enum):
    GET = 1
    SET = 2
    DEL = 3
    EXISTS = 4
    PING = 5
    ECHO = 6

class MiniRedis:
    
    def __init__(self):
        self.store  : dict[bytes, bytes] = {}
        self.supported_commands = {
            'get' : CMD.GET,
            'set' : CMD.SET,
            'del' : CMD.DEL,
            'ping' : CMD.PING,
            'echo' : CMD.ECHO,
            'exists' : CMD.EXISTS
        }

    @staticmethod
    def _check_arg_count(params: list[str], name: str, expected: int) -> None:
        """Raise ValueError unless the command has exactly `expected` arguments."""
        if len(params) - 1 != expected:
            raise ValueError(
                f"Invalid number of arguments for {name}: "
                f"expected {expected}, got {len(params) - 1}."
            )

    def process_command(self, cmd : str):
        if not isinstance(cmd, str):
            raise TypeError(f"Command must be a str, not {type(cmd).__name__}.")

        params = cmd.split()
        if not params:
            raise ValueError("Empty command.")
        params[0] = params[0].lower()
        if params[0] not in self.supported_commands:
            raise ValueError(f"Command not supported: {params[0]!r}.")
        
        cmd_type = self.supported_commands[params[0]]
        match cmd_type:
            case CMD.GET:
                self._check_arg_count(params, "GET", 1)
                key = params[1].encode("utf-8")
                return self.store.get(key)
            case CMD.SET:
                self._check_arg_count(params, "SET", 2)
                key = params[1].encode("utf-8")
                val = params[2].encode("utf-8")
                self.store[key] = val
                return b"OK"
            case CMD.DEL:
                self._check_arg_count(params, "DEL", 1)
                key = params[1].encode("utf-8")
                if key not in self.store:
                    return 0
                del self.store[key]
                return 1
            case CMD.PING:
                self._check_arg_count(params, "PING", 0)
                return b"PONG"
            case CMD.ECHO:
                if len(params) < 2:
                    raise ValueError(
                        "Invalid number of arguments for ECHO: expected at least 1, got 0."
                    )
                params = cmd.split(maxsplit=1)
                return params[1].encode("utf-8")
            case CMD.EXISTS:
                self._check_arg_count(params, "EXISTS", 1)
                key = params[1].encode("utf-8")
                return 1 if key in self.store else 0



if __name__ == "__main__":
    n = input()
    n = int(n)
    my_reddis = MiniRedis()
    for i in range(n) :
        s = input()
        try:
            print(my_reddis.process_command(s))
        except ValueError as e:
            print(f"ERR {e}")
