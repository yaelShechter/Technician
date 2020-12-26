import socket
from server_functions import *

SERVER_IP = '0.0.0.0'


class server:
    def __init__(self, ip, port):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((ip, port))

    def run(self):
        self.__server_socket.listen()
        print("Server is up and running")
        client_socket, _ = self.__server_socket.accept()
        print("Client connected")

        while True:
            command, params = handle_message(client_socket)
            handle_client_request(command, params)

            if command == 'SEND_PHOTO':
                send_real_photo(client_socket)
            elif command == 'EXIT':
                break
            else:
                send_response(client_socket)

            client_socket.recv(1024)

        print("Closing connection")
        client_socket.close()
        self.__server_socket.close()


def main():
    my_server = server(SERVER_IP, protocol.PORT)
    my_server.run()


if __name__ == '__main__':
    main()
