class MiniRESP:
    def __init__(self):
        pass

    def __readBulkString__(self, idx : int, data : bytes) -> list[int, bytes]:
        curData = data[idx:]
        parts = curData.split(b"\r\n", maxsplit=1)
        
        if not parts[0].startswith(b"$"):
            raise ProtocolError("Expected an array")
        
        strLen = int(parts[0][1:])
        idx += len(parts[0]) + 2
        
        if idx >= len(data) :
            # TODO : raise an error
            return
        
        ans : bytes = data[idx : idx + strLen]
        
        idx += strLen + 2
        return [idx, ans]
        
        
    
    def __readArray__(self, idx : int, data : bytes) -> int :
        if idx >= len(data) :
            return

        parts = data.split(b"\r\n", maxsplit=1)

        # 1. Check whether the header is complete
        if len(parts) < 2:
            raise IncompleteRequest("Incomplete array header")

        # 2. Check the array prefix
        if not parts[0].startswith(b"*"):
            raise ProtocolError("Expected an array")

        # 3. Check whether the length is numeric
        if not parts[0][1:].isdigit():
            raise ProtocolError("Invalid array length")

        arrLength = int(parts[0][1:])

        if arrLength == 0:
            raise ProtocolError("Empty command array")
        
        print(arrLength)
        ans = []
        idx = len(parts[0]) + 2
        for i in range(arrLength) :
            curType = data[idx]
            if curType != ord('$') :
                # TODO : raise error
                return
            idx, curEl = self.__readBulkString__(idx, data)
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