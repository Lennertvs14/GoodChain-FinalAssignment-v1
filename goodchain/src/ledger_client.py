from database import Database
from ledger_server import HEADER_SIZE, DATA_FORMAT
import pickle
from transaction_block import TransactionBlock
import socket


class LedgerClient:
    database = Database()

    def __init__(self, corresponding_server_port):
        self.host = socket.gethostbyname(socket.gethostname())
        self.corresponding_server_port = corresponding_server_port

    def broadcast_ledger_change(self, new_block: TransactionBlock):
        for server_port in self.database.get_ledger_servers():
            # We do not need to broadcast the new block to ourselves
            if server_port != self.corresponding_server_port:
                try:
                    # Create a new socket for each connection
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        # Connect to peer address
                        s.connect((self.host, int(server_port)))
                        # Send new block
                        if new_block:
                            # Prepare data
                            block_data = pickle.dumps(new_block)
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
                    print(f"Connection to this server {server_port} cannot be established.")
