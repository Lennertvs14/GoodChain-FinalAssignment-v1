import select
import socket
from threading import Thread


HOST = socket.gethostbyname('localhost')
PORT = 5050
HEADER_SIZE = 64
DATA_FORMAT = 'utf-8'
DISCONNECTION_MESSAGE = ':Q'
DEFAULT_BUFFER_SIZE = 1024

server_is_running = False


def handle_client(connection, address):
    # Get client info
    client_user_name = connection.recv(DEFAULT_BUFFER_SIZE).decode(DATA_FORMAT)
    print(f'New connection {client_user_name} @ {address}')

    # Get data
    client_wants_to_interact = True
    while client_wants_to_interact:
        # Initialize buffer
        read_buffer, write_buffer, error_buffer = select.select([connection], [], [])

        if len(read_buffer) > 0:
            data_length = int(connection.recv(HEADER_SIZE).decode(DATA_FORMAT))
            if data_length > 0:
                data = connection.recv(data_length).decode(DATA_FORMAT)
                # TODO: Update ledger by client data (if it's valid)
                print(f"{client_user_name} @ {address}: {data}." + "\n")
        else:
            # Client did not send anything
            client_wants_to_interact = False

    # Client is handled
    connection.close()


def start():
    # Start ledger server with new thread to avoid blocking the main thread
    server_thread = Thread(target=listen, daemon=True)
    server_thread.start()


def listen():
    global server_is_running
    # Find an available port, start with 5050
    found_available_port = False
    while found_available_port is False:
        try:
            # Create a new socket using the AF_INET address family (IPv4) and SOCK_STREAM socket type (TCP)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                # Try to bind socket to current port
                server_socket.bind((HOST, PORT))
                # Successful bind
                found_available_port = True
                # Start listening
                server_socket.listen()
                server_is_running = True
                while server_is_running:
                    # Client established connection, accept and handle it
                    conn, addr = server_socket.accept()
                    thread = Thread(target=handle_client, args=(conn, addr))
                    thread.start()
        except socket.error:
            # Binding failed, so current port is unavailable
            continue # -> server is already listening on this machine


def stop():
    global server_is_running
    # Stop the running server
    server_is_running = False
