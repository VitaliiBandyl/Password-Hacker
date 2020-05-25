import itertools
import socket
import sys
from typing import Iterable, Generator


def brute_force(charset: Iterable, minlength: int, maxlength: int) -> Generator:
    """Takes an iterable object with a sequence of possible characters.
        Minimum and maximum combination length.
        Returns a generator that will sort all possible combinations"""
    return (''.join(char)
            for char in itertools.chain.from_iterable(itertools.product(charset, repeat=i)
                                                      for i in range(minlength, maxlength + 1)))


def main():
    ip_address = sys.argv[1]
    port = int(sys.argv[2])
    address = (ip_address, port)
    charset = 'abcdefjhigklmnopqrstuvwxyz1234567890'
    password_generator = brute_force(charset, 1, 16)

    with socket.socket() as connection:
        connection.connect(address)
        for password in password_generator:
            encoded_password = password.encode()
            connection.send(encoded_password)
            response = connection.recv(1024)
            response = response.decode()
            if response == 'Connection success!':
                print(password)
                break


if __name__ == '__main__':
    main()
