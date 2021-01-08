import os
import glob
import shutil
import pyautogui
import subprocess

import socket
import protocol

SERVER_IP = '0.0.0.0'
PHOTO_PATH = ''

FIRST_FILE_PATH_INDEX = 0
SECOND_FILE_PATH_INDEX = 1

DIRECTORY_PATH_INDEX = 0
EXECUTABLE_PARAM_INDEX = 0

DATA_SIZE = 1024


def handle_message(client_socket):
    command = protocol.receive_command(client_socket)
    response = handle_client_request(command)
    client_socket.send(protocol.serialize_response(response))
    return command


def handle_client_request(command):
    params = command.data.split(' ')
    return {'TAKE_SCREENSHOT': lambda: take_screenshot(),
            'SEND_PHOTO': lambda: send_photo_size(),
            'DIR': lambda: files_list_in_directory(params[DIRECTORY_PATH_INDEX]),
            'DELETE': lambda: delete(params[FIRST_FILE_PATH_INDEX]),
            'COPY': lambda: copy(params[FIRST_FILE_PATH_INDEX], params[SECOND_FILE_PATH_INDEX]),
            'EXECUTE': lambda: execute(params),
            'EXIT': lambda: 'Exiting program'
            }[command.header.type]()


def take_screenshot():
    try:
        pyautogui.screenshot().save(PHOTO_PATH)
        return 'Screenshot taken successfully'
    except Exception as error:
        return f'Error in taking screenshot: {error}'


def send_photo_size():
    try:
        with open(PHOTO_PATH, 'rb') as photo:
            photo_size = photo.read()
            return str(len(photo_size))
    except Exception as error:
        return f'Error in sending photo size: {error}'


def send_photo(client_socket):
    with open(PHOTO_PATH, 'rb') as photo:
        client_socket.send(photo.read())


def files_list_in_directory(directory_path):
    try:
        all_files = r'\*.*'
        directory_path = f'{directory_path}{all_files}'
        return str(glob.glob(directory_path))
    except FileNotFoundError as error:
        return f'Error in printing directory process: {error}'


def delete(file_to_delete_path):
    try:
        os.remove(file_to_delete_path)
        return 'File deleted successfully'
    except FileNotFoundError as error:
        return f'Error in deleting file: {error}'


def copy(copied_file_path, pasted_file_path):
    try:
        shutil.copy(copied_file_path, pasted_file_path)
        return 'Filed copied successfully'
    except FileNotFoundError or PermissionError as error:
        return f'Error in copying process: {error}'


def execute(executable_name):
    try:
        subprocess.call(executable_name)
        return 'Executed successfully'
    except subprocess.CalledProcessError as error:
        return f'Error in executing process: {error}'


def send_bad_command_message(client_socket):
    response = 'Bad command or parameters'
    client_socket.send(protocol.serialize_response(response))


def send_error_response(client_socket):
    response = 'Packet not according to protocol'
    client_socket.send(protocol.serialize_response(response))


def clear_client_socket(client_socket):
    client_socket.recv(DATA_SIZE)


class server:
    def __init__(self, ip, port):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((ip, port))
        self._should_terminate = False

    def run(self):
        self._server_socket.listen()
        print("Server is up and running")
        client_socket, _ = self._server_socket.accept()
        print("Client connected")

        while not self._should_terminate:
            command = handle_message(client_socket)  # sends message back to client
            self.handle_special_commands(command.header.type, client_socket)

        clear_client_socket(client_socket)

        print("Closing connection")
        client_socket.close()
        self._server_socket.close()

    def handle_special_commands(self, command_name, client_socket):
        if command_name == 'SEND_PHOTO':
            send_photo(client_socket)
        if command_name == 'EXIT':
            self._should_terminate = True


def main():
    my_server = server(SERVER_IP, protocol.PORT)
    my_server.run()


if __name__ == '__main__':
    main()
