import select
import socket
from threading import Thread


HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
HEADER_SIZE = 64
DATA_FORMAT = 'utf-8'
DISCONNECTION_MESSAGE = ':Q'
DEFAULT_BUFFER_SIZE = 1024

server_is_running = False


def handle_client(connection):
    try:
        # Get client info
        client_user_name = connection.recv(DEFAULT_BUFFER_SIZE).decode(DATA_FORMAT)
        while True:
            # Initialize buffer
            read_buffer, _, _ = select.select([connection], [], [])
            if len(read_buffer) > 0:
                # Receive the header to determine data length
                header = connection.recv(HEADER_SIZE).decode(DATA_FORMAT)
                if not header:
                    break
                data_length = int(header.strip())
                if data_length > 0:
                    data = connection.recv(data_length).decode(DATA_FORMAT)
                    if data:
                        # TODO: Update ledger by client data (if it's valid)
                        print(f"Received new block:\n{data}")
                    break
    finally:
        # Client is handled
        connection.close()


def start():
    # Start ledger server with new thread to avoid blocking the main thread
    server_thread = Thread(target=listen, daemon=True)
    server_thread.start()


def listen():
    global server_is_running
    # Find an available port, start with 5050
    try:
        # Create a new socket using the AF_INET address family (IPv4) and SOCK_STREAM socket type (TCP)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # Try to bind socket to current port
            server_socket.bind((HOST, PORT))
            # Successful bind
            # Start listening
            server_socket.listen()
            server_is_running = True
            while server_is_running:
                # Client established connection, accept and handle it
                conn, addr = server_socket.accept()
                thread = Thread(target=handle_client, args=(conn, ))
                thread.start()
    except socket.error:
        # Binding failed, so current port is unavailable
        pass # -> server is already listening on this machine


def stop():
    global server_is_running
    # Stop the running server
    server_is_running = False
