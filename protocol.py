from construct import *

LENGTH_FIELD_SIZE = 4
PORT = 8820

CommandType = Enum(Byte, TAKE_SCREENSHOT=0, SEND_PHOTO=1, DIR=2, DELETE=3, COPY=4, EXECUTE=5, EXIT=6)
CommandHeader = Struct('size' / Int32ub, 'type' / CommandType)

command = Struct('header' / CommandHeader, 'command_data' / GreedyBytes)


def check_cmd(command, params):
    if command in ['TAKE_SCREENSHOT', 'SEND_PHOTO', 'EXIT'] and len(params) == 0 \
            or command in ['DIR', 'DELETE', 'EXECUTE'] and len(params) == 1 \
            or command == 'COPY' and len(params) == 2:
        return True
    return False


def create_msg(data):
    if data:
        print(CommandHeader.build(dict(size=len(str(data)) + CommandHeader.sizeof(), type=CommandType.TAKE_SCREENSHOT)))
        print(CommandHeader.parse(b'\x00\x00\x00\x14\x00'))
        return str(len(str(data))).zfill(LENGTH_FIELD_SIZE) + str(data)


def get_message(my_socket):
    message = my_socket.recv(1024).decode()
    return message[:LENGTH_FIELD_SIZE].isnumeric(), message[LENGTH_FIELD_SIZE:]
