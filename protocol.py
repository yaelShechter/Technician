from construct import *

LENGTH_FIELD_SIZE = 4
COMMAND_NAME_INDEX = 0
BYTES_TO_READ = 1024
PORT = 8820

CommandType = Enum(Byte,
                   TAKE_SCREENSHOT=0,
                   SEND_PHOTO=1,
                   DIR=2,
                   DELETE=3,
                   COPY=4,
                   EXECUTE=5,
                   EXIT=6)

CommandHeader = Struct(
    'type' / CommandType,
    'data_size' / Int32ub
)

Command = Struct(
    'header' / CommandHeader,
    'data' / PascalString(Int32ub, 'utf8')
)

Response = Struct(
    'data' / PascalString(Int32ub, 'utf8')
)


def serialize_response(response):
    return Response.build(dict(data=response))


def receive_response(my_socket):
    raw_size = my_socket.recv(4)
    parsed_size = Int32ub.parse(raw_size)
    raw_data = my_socket.recv(parsed_size)
    return Response.parse(raw_size + raw_data)


def get_command_name(command):
    return command.split(" ")[COMMAND_NAME_INDEX]


def get_command_params(command):
    return command.split(" ")[COMMAND_NAME_INDEX + 1:]


def serialize_command(command):
    if command:
        command_name = get_command_name(command)
        command_params = ''.join(get_command_params(command))

        return Command.build(dict(
            header=dict(type=command_name, data_size=len(command_params)+4),
            data=command_params
        ))


def receive_command(my_socket):
    raw_header = my_socket.recv(CommandHeader.sizeof())
    parsed_header = CommandHeader.parse(raw_header)
    print(parsed_header)
    raw_data = my_socket.recv(parsed_header.data_size)
    print(Command.parse(raw_header + raw_data))
    return Command.parse(raw_header + raw_data)
