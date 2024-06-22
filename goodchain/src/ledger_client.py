from server import HEADER_SIZE, DATA_FORMAT
import pickle
from transaction_block import TransactionBlock
import socket


class LedgerClient:
    def __init__(self, corresponding_server):
        self.host = socket.gethostbyname(socket.gethostname())
        self.corresponding_server = corresponding_server

    def broadcast_change(self, crud_operation, block: TransactionBlock):
                try:
                    # Create a new socket for each connection
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        # Connect to peer address
                        s.connect((self.host, int(server_port)))
                        # Send the block
                        if block:
                            # Prepare data
                            block_data = pickle.dumps((crud_operation, block))
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
        for server_port in self.corresponding_server.get_servers(include_own_server=False):
