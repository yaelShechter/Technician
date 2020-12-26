import os
import glob
import shutil
import pyautogui
import subprocess

import protocol

PHOTO_PATH = r'C:\Users\yaels\Desktop\Networks\screen.jpg'

COMMAND = 0
PARAMS = 1

COPIED_FILE = 0
PASTED_FILE = 1
DELETED_FILE = 0
DIRECTORY = 0
EXECUTABLE = 0


def handle_message(client_socket):
    valid_input, message = protocol.get_message(client_socket)
    if valid_input:
        command, params = slice_message(message)
        print(command)
        print(params)
        if is_valid_params(command, params):
            response = handle_client_request(command, params)
            message = protocol.create_msg(response)
            client_socket.send(message.encode())
            print("THE PARAMS ARE VALID")

            return command, params


def slice_message(message):
    return message.split()[COMMAND], message.split()[PARAMS:]


def is_valid_params(command, params):
    if protocol.check_cmd(command, params):
        if command in ['DELETE', 'COPY']:
            return os.path.isfile(params[0])
        elif command == 'DIR':
            return os.path.isdir(params[0])
        return True

    return False


def handle_client_request(command, params):
    return {'TAKE_SCREENSHOT': lambda: take_screenshot(),
            'SEND_PHOTO': lambda: send_photo(),
            'DIR': lambda: files_list_in_dir(params),
            'DELETE': lambda: delete(params),
            'COPY': lambda: copy(params),
            'EXECUTE': lambda: execute(params),
            'EXIT': lambda: 'Exiting program'
            }[command]()


def take_screenshot():
    try:
        pyautogui.screenshot().save(PHOTO_PATH)
        return 'Screenshot taken successfully'
    except Exception as e:
        return f'Error in taking screenshot: {e}'


def send_photo():
    try:
        with open(PHOTO_PATH, 'rb') as photo:
            photo_size = photo.read()
            return len(photo_size)
    except Exception as e:
        return f'Error in sending photo size: {e}'


def send_real_photo(client_socket):
    with open(PHOTO_PATH, 'rb') as photo:
        client_socket.send(photo.read())


def files_list_in_dir(params):
    try:
        all_files = r'\*.*'
        directory_path = f'{params[DIRECTORY]}{all_files}'
        return glob.glob(directory_path)
    except Exception as e:
        return f'Error in printing directory process: {e}'


def delete(params):
    try:
        os.remove(params[DELETED_FILE])
        return 'File deleted successfully'
    except Exception as e:
        return f'Error in deleting file: {e}'


def copy(params):
    try:
        shutil.copy(params[COPIED_FILE], params[PASTED_FILE])
        return 'Filed copied successfully'
    except Exception as e:
        return f'Error in copying process: {e}'


def execute(params):
    try:
        subprocess.call(params[EXECUTABLE])
        return 'Executed successfully'
    except Exception as e:
        return f'Error in executing process: {e}'


def send_bad_command_message(client_socket):
    response = 'Bad command or parameters'
    client_socket.send(response.encode())


def send_response(client_socket):
    response = 'Packet not according to protocol'
    client_socket.send(response.encode())
