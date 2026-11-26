from main import CMD

class ProtocolError(ValueError):
    """The bytes are not valid RESP. The client sent garbage."""


class IncompleteRequest(Exception):
    """The bytes are valid so far, but the command isn't complete yet. Read more and retry."""

class MiniRESP:
    CRLF = b"\r\n"
    NULL_BULK_STR = b"$-1" + CRLF
    def __init__(self):
        pass
    
    def _read_line(self, idx : int, data : bytes, prefix : bytes, what : str) -> tuple[bytes, int]:
        if idx >= len(data):
            raise IncompleteRequest("Missing header")

        if not data[idx:].startswith(prefix):
            raise ProtocolError(f"Expected {what} ({prefix!r}), got {data[idx:idx + len(prefix)]!r}")
        end = data.find(self.CRLF, idx)
        if end == -1:
            raise IncompleteRequest("Line not terminated yet")
        
        return data[idx: end], end + len(self.CRLF)
    
    def _parse_len(self, line : bytes, prefix : bytes, what : str) -> int :
        digits = line[len(prefix):]
        if not digits.isdigit() :
            raise ProtocolError(f"Invalid {what} length: {digits!r}")
        return int(digits)

    def _read_bulk_string(self, idx : int, data : bytes) -> tuple[bytes, int]:
        header, idx = self._read_line(idx, data, b"$", "Bulk string")
        strLen = self._parse_len(header, b"$", "Bulk string")
        
        end = idx + strLen
        if len(data) < end:
            raise IncompleteRequest("Bulk string data not fully received")
        
        delimiter = data[end:end + len(self.CRLF)]

        if not self.CRLF.startswith(delimiter):
            raise ProtocolError("Invalid CRLF")

        if len(delimiter) < len(self.CRLF):
            raise IncompleteRequest("Incomplete CRLF")
        return data[idx:end], end + len(self.CRLF)        

    
    def parser(self, data : bytes, idx : int = 0) -> tuple[list[bytes], int]:
        if idx >= len(data):
            raise IncompleteRequest("Empty buffer")

        header, idx = self._read_line(idx, data, b"*", "*")
        arrLength = self._parse_len(header, b"*", "Array")

        ans = []
        for _ in range(arrLength) :
            arg, idx = self._read_bulk_string(idx, data)
            ans.append(arg)

        return ans, idx
    
    def _serialize_bulk_string(self, data : bytes) -> bytes:
        length = str(len(data)).encode()
        return b"$" + length + self.CRLF + data + self.CRLF
    
    def _serialize_simple_string(self, data : bytes) -> bytes:
        return b"+" + data + self.CRLF
    
    def _serialize_int(self, data : int) -> bytes:
        return b":" + str(data).encode() + self.CRLF
    
    def _serialize_error(self, data : bytes) -> bytes:
        return b"-ERR " + data + self.CRLF
        
    
    def serialize(self, cmd_type : CMD, result : bytes | int | None) -> bytes:
        match cmd_type:
            case CMD.GET:
                if result is not None and type(result) is not bytes:
                    return self._serialize_error(b"The result of GET should be either None or bytes")
                if result is not None:
                    return self._serialize_bulk_string(result)
                else:
                    return self.NULL_BULK_STR
            case CMD.SET:
                if type(result) is not bytes or result != b"OK" :
                    return self._serialize_error(b"The result of SET is invalid")
                return self._serialize_simple_string(result)
            case CMD.DEL | CMD.EXISTS:
                if type(result) is not int or result not in (0, 1):
                    return self._serialize_error(b"Invalid command result")
                return self._serialize_int(result)
            case CMD.PING:
                if type(result) is not bytes or result != b"PONG":
                    return self._serialize_error(b"The result of PONG is invalid")
                return self._serialize_simple_string(result)
            case CMD.ECHO:
                if type(result) is not bytes :
                    return self._serialize_error(b"The result of ECHO is invalid")
                return self._serialize_bulk_string(result)
            case _:
                return self._serialize_error(b"Unsupported command")
    

if __name__ == "__main__":
    pars = MiniRESP()
    print(pars.parser(b"*3\r\n$3\r\nSET\r\n$1\r\nk\r\n$0\r\n\r\n"))
    print(pars.parser(b"*2\r\n$3\r\nGET\r\n$4\r\nname\r\n"))
    print(pars.parser(b"*1\r\n$4\r\nPING\r\n"))
    print(pars.parser(b"*2\r\n$4\r\nECHO\r\n$4\r\nA\r\nB\r\n"))
    try:
        print(pars.parser(b"*2"))
    except IncompleteRequest:
        print("here")
    print(pars.parser(b"*1\r\n$3\r\nGETx"))
        