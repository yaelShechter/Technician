import socket
import protocol

CLIENT_IP = '127.0.0.1'
SAVED_PHOTO_LOCATION = ''

NAME_INDEX = 0
PHOTO_CHUNK_SIZE = 1024

COMMANDS = ['TAKE_SCREENSHOT', 'SEND_PHOTO', 'DIR', 'DELETE', 'COPY', 'EXECUTE', 'EXIT']

command_by_length = {
    1: ['TAKE_SCREENSHOT', 'SEND_PHOTO', 'EXIT'],
    2: ['DIR', 'DELETE', 'EXECUTE'],
    3: ['COPY']
}


def is_valid_input(command_string):
    splitted_command = command_string.split(" ")
    command_name = splitted_command[NAME_INDEX]
    command_length = len(splitted_command)
    return command_name in command_by_length[command_length]


class client:
    def __init__(self, ip, port):
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_socket.connect((ip, port))
        self._should_terminate = False

    def run(self):
        print('Welcome to remote computer application. Available commands are:')
        print("\n".join(COMMANDS))

        while not self._should_terminate:
            command = input("Please enter command:\n")
            if is_valid_input(command):
                self._client_socket.send(protocol.serialize_command(command))
                self.handle_server_response(command)

            else:
                print("Not a valid command, or missing parameters")

        self._client_socket.close()

    def receive_photo(self, size):
        is_photo_sent = False
        current_size = size
        with open(SAVED_PHOTO_LOCATION, 'wb') as screenshot:
            screenshot.write(self._client_socket.recv(size))
        print("Photo sent")

    def handle_server_response(self, command):
        message = protocol.receive_response(self._client_socket)
        if command == 'SEND_PHOTO':
            photo_size = int(message.data)
            self.receive_photo(photo_size)
        elif command == 'EXIT':
            self._should_terminate = True
        else:
            print(message.data)


def main():
    my_client = client(CLIENT_IP, protocol.PORT)
    my_client.run()


if __name__ == '__main__':
    main()
