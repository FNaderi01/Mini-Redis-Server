class MiniRESP:
    CRLF = b"\r\n"
    def __init__(self):
        pass
    
    def __readLine__(self, idx : int, data : bytes) -> tuple[bytes, int] :
        end = data.find(self.CRLF, idx)
        if end == -1 :
            raise IncompleteRequest("Line not terminated yet")
        
        return data[idx: end], end + len(self.CRLF)
    
    def __parseLen__(self, line : bytes, prefix : bytes, what : str) -> int :
        if not line.startswith(prefix) :
            raise ProtocolError(f"Expected {what} ({prefix!r}), got {line[:len(prefix)]!r}")

        digits = line[len(prefix):]
        if not digits.isdigit() :
            raise ProtocolError(f"Invalid {what} length: {digits!r}")
        return int(digits)

    def __readBulkString__(self, idx : int, data : bytes) -> list[bytes, int]:
        header, idx = self.__readLine__(idx, data)
        
        if not header.startswith(b"$"):
            raise ProtocolError("Expected an array")

        if not header[1:].isdigit():
            raise ProtocolError("Invalid array length")
        
        strLen = int(header[1:])
        
        end = idx + strLen
        if len(data) < end + len(self.CRLF):
            raise IncompleteRequest("Bulk string data not fully received")
        
        if data[end:end + len(self.CRLF)] != self.CRLF:
            raise ProtocolError("Bulk string is not followed by CRLF")
        return data[idx:end], end + len(self.CRLF)
        
        
    
    def __readArray__(self, idx : int, data : bytes) -> int :
        if idx >= len(data) :
            return

        header, idx = self.__readLine__(idx, data)


        # 1. Check the array prefix
        if not header.startswith(b"*"):
            raise ProtocolError("Expected an array")

        # 2. Check whether the length is numeric
        if not header[1:].isdigit():
            raise ProtocolError("Invalid array length")

        arrLength = int(header[1:])

        if arrLength == 0:
            raise ProtocolError("Empty command array")
        
        print(arrLength)
        ans = []
        for i in range(arrLength) :
            curType = data[idx]
            if curType != ord('$') :
                # TODO : raise error
                return
            curEl, idx = self.__readBulkString__(idx, data)
            ans.append(curEl)
        return ans

    
    def parser(self, cmd : bytes) -> list[bytes] :
        return self.__readArray__(0, cmd)
    

if __name__ == "__main__":
    pars = MiniRESP()
    print(pars.parser(b"*3\r\n$3\r\nSET\r\n$1\r\nk\r\n$0\r\n\r\n"))
    print(pars.parser(b"*2\r\n$3\r\nGET\r\n$4\r\nname\r\n"))
    print(pars.parser(b"*1\r\n$4\r\nPING\r\n"))
    print(pars.parser(b"*2\r\n$4\r\nECHO\r\n$4\r\nA\r\nB\r\n"))