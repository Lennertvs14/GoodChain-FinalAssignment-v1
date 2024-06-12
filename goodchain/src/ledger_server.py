from ledger import Ledger
import pickle
import select
import socket
from threading import Thread
from time import sleep, time


HEADER_SIZE = 64
DATA_FORMAT = 'utf-8'
DEFAULT_BUFFER_SIZE = 1024


def handle_client(connection):
    try:
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
                    new_block = connection.recv(data_length)
                    if new_block:
                        # Deserialize
                        new_block = pickle.loads(new_block)
                        # Add new block to ledger
                        if new_block.block_hash:
                            Ledger.add_block(new_block)
                    break
    finally:
        # Client is handled
        connection.close()


class LedgerServer:
    owner = None

    def __init__(self):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 5050
        self.server_is_running = False
        self.available_port_is_found = False

    def start_server(self):
        # Start ledger server with new thread to avoid blocking the main thread
        server_thread = Thread(target=self.listen, daemon=True)
        server_thread.start()
        start_time = time()

        # Wait until an available port is found
        while self.available_port_is_found is False:
            # Check if we've been waiting for more than 1 minute
            if time() - start_time > 60:
                raise Exception("Timeout: Could not find an available port.")
            sleep(0.1)

        print(f"Server is listening on {self.port}")

    def listen(self):
        # Find an available port
        while self.available_port_is_found is False:
            try:
                # Create a new socket using the AF_INET address family (IPv4) and SOCK_STREAM socket type (TCP)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                    # Try to bind socket to current port
                    server_socket.bind((self.host, self.port))
                    # Successful bind
                    self.available_port_is_found = True
                    # Start listening
                    server_socket.listen()
                    self.server_is_running = True
                    while self.server_is_running:
                        # Client established connection, accept and handle it
                        conn, addr = server_socket.accept()
                        thread = Thread(target=handle_client, args=(conn,))
                        thread.start()
            except socket.error:
                # Binding failed, so current port is unavailable
                self.port += 1

    def stop_server(self):
        # Stop the running server
        self.server_is_running = False
