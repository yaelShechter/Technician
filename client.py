import socket
import protocol

CLIENT_IP = '127.0.0.1'
SAVED_PHOTO_LOCATION = r'C:\Users\yaels\Desktop\Networks\screenshot.jpg'


class client:
    def __init__(self, ip, port):
        self.__my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__my_socket.connect((ip, port))

    def run(self):
        print('Welcome to remote computer application. Available commands are:\n')
        print('TAKE_SCREENSHOT\nSEND_PHOTO\nDIR\nDELETE\nCOPY\nEXECUTE\nEXIT')

        while True:
            cmd = input("Please enter command:\n")
            if protocol.check_cmd(cmd.split()[0], cmd.split()[1:]):
                packet = protocol.create_msg(cmd)
                self.__my_socket.send(packet.encode())
                self.handle_server_response(cmd)
                if cmd == 'EXIT':
                    break
            else:
                print("Not a valid command, or missing parameters\n")

        self.__my_socket.close()

    def receive_photo(self, size):
        current_size = size
        with open(SAVED_PHOTO_LOCATION, 'wb') as screenshot:
            while True:
                line = self.__my_socket.recv(1024)
                current_size -= 1024
                if current_size <= 0:
                    break
                screenshot.write(line)
        print("Photo sent")

    def handle_server_response(self, cmd):
        """
        Receive the response from the server and handle it, according to the request
        For example, DIR should result in printing the contents to the screen,
        Note- special attention should be given to SEND_PHOTO as it requires and extra receive
        """
        valid, message = protocol.get_message(self.__my_socket)
        command = cmd.split()[0]
        if command == 'SEND_PHOTO':
            self.receive_photo(int(message))
        else:
            print(message)


def main():
    my_client = client(CLIENT_IP, protocol.PORT)
    my_client.run()


if __name__ == '__main__':
    main()
