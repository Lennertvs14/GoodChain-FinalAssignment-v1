from abc import ABC, abstractmethod
import pickle
import select
import socket
from threading import Thread
from time import sleep, time

HEADER_SIZE = 64
DATA_FORMAT = 'utf-8'
DEFAULT_BUFFER_SIZE = 1024
CRUD = {
    "ADD": "ADD",
    "UPDATE": "UPDATE",
    "DELETE": "DELETE",
    "REGISTER": "REGISTER"
}


class Server(ABC):
    """ Base class for servers in client/server model context """
    default_port = None
    server_data_file_path = None

    def __init__(self, port):
        self.port = port
        self.host = socket.gethostbyname(socket.gethostname())
        self.server_is_running = False
        self.available_port_is_found = False

    @abstractmethod
    def handle_client(self, connection):
        pass

    @staticmethod
    def get_client_data(connection):
        data = None
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
                        data = connection.recv(data_length)
                        break
        finally:
            # Client is handled
            connection.close()
            return pickle.loads(data)

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

        # Whisper to network
        self.add_server()
        self.announce_presence()

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
                        thread = Thread(target=self.handle_client, args=(conn,))
                        thread.start()
            except socket.error:
                # Binding failed, so current port is unavailable
                self.port += 1

    def add_server(self, new_server_port=None):
        """ Adds server's port to the file """
        if new_server_port:
            server = new_server_port
        else:
            server = self.port
        server_is_new = not (self.get_servers(include_own_server=True).__contains__(server))
        if self.server_data_file_path and server_is_new:
            with open(self.server_data_file_path, "ab") as f:
                pickle.dump(server, f)

    def announce_presence(self):
        """ Whispers the server's port to network """
        known_servers = self.get_servers(include_own_server=False)
        if len(known_servers) < 1 and self.default_port:
            # Count down to default port to discover unknown running servers.
            temp = self.port
            while temp > self.default_port:
                temp -= 1
                known_servers.append(temp)
                self.add_server(temp)

        for server_port in known_servers:
            try:
                # Create a new socket for each connection
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # Connect to peer address
                    s.connect((self.host, int(server_port)))
                    # Prepare data
                    block_data = pickle.dumps((CRUD.get("REGISTER"), self.port))
                    data_length = len(block_data)
                    # Create header
                    header = str(data_length).encode(DATA_FORMAT)
                    header += b' ' * (HEADER_SIZE - len(header))
                    # Send header
                    s.send(header)
                    # Send the actual data
                    s.send(block_data)
            except OSError as os_error:
                # Connection to this server cannot be established.
                pass
            finally:
                s.close()

    def get_servers(self, include_own_server=True):
        """ Returns a list of servers from the file """
        servers = []
        try:
            with open(self.server_data_file_path, "rb") as server_data:
                while True:
                    server_port = pickle.load(server_data)
                    if include_own_server or int(server_port) != int(self.port):
                        servers.append(server_port)
        except FileNotFoundError:
            # There are no servers yet.
            pass
        except EOFError:
            # No more lines to read from file.
            pass
        return servers

    def stop_server(self):
        # Stop the running server
        self.server_is_running = False
