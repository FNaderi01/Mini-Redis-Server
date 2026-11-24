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
        self.store = {}
        self.supported_commands = {
            'get' : CMD.GET,
            'set' : CMD.SET,
            'del' : CMD.DEL,
            'ping' : CMD.PING,
            'echo' : CMD.ECHO,
            'exists' : CMD.EXISTS
        }
        print("success")


    def process_command(self, cmd : str):
        params = cmd.split(' ')
        params[0] = params[0].lower()
        if self.supported_commands.get(params[0]) is None:
            print("Command not supported")
            return
        
        cmd_type = self.supported_commands[params[0]]
        match cmd_type:
            case CMD.GET:
                if len(params) != 2:
                    print("Invalid number of arguments for GET command. Your command: %s", cmd)
                    return
                key = params[1].encode("utf-8")
                return self.store.get(key)
            case CMD.SET:
                if len(params) != 3:
                    print("Invalid number of arguments for SET command. Your command: %s", cmd)
                    return
                key = params[1].encode("utf-8")
                val = params[2].encode("utf-8")
                self.store[key] = val
                return b"OK"
            case CMD.DEL:
                if len(params) != 2:
                    print("Invalid number of arguments for DEL command. Your command: %s", cmd)
                    return
                key = params[1].encode("utf-8")
                
                if self.store.get(key) is None:
                    return 0
                del self.store[key]
                return 1
            case CMD.PING:
                if len(params) != 1:
                    print("Invalid number of arguments for PING command. Your command: %s", cmd)
                    return
                print("PONG")
                return
            case CMD.ECHO:
                if len(params) != 2:
                    print("Invalid number of arguments for ECHO command. Your command: %s", cmd)
                    return
                print(cmd)
                return
            case CMD.EXISTS:
                if len(params) != 2:
                    print("Invalid number of arguments for EXISTS command. Your command: %s", cmd)
                    return
                key = params[1].encode("utf-8")
                if self.store.get(key) is None :
                    return 0
                return 1



if __name__ == "__main__":
    n = input()
    n = int(n)
    my_reddis = MiniRedis()
    for i in range(n) :
        s = input()
        print(type(s))
        print(my_reddis.process_command(s))