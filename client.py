import socket


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 25565)
    client_socket.connect(server_address)

    try:
        message = "Hello World!"
        client_socket.sendall(message.encode())
        print(f"Отправлено серверу: {message}")

        data = client_socket.recv(1024)
        print(f"Получено от сервера: {data.decode()}")

    finally:
        client_socket.close()


if __name__ == "__main__":
    start_client()