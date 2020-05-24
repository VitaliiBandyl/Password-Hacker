import socket
import sys


def main():
    ip_address = sys.argv[1]
    port = int(sys.argv[2])
    address = (ip_address, port)
    message = sys.argv[3].encode()

    with socket.socket() as connection:
        connection.connect(address)
        connection.send(message)
        response = connection.recv(1024)
        response = response.decode()
        print(response)


if __name__ == '__main__':
    main()
