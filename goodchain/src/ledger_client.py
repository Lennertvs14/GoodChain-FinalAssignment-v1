from transaction_block import TransactionBlock
from ledger_server import PORT
import socket


HEADER_SIZE = 64
DATA_FORMAT = 'utf-8'


class LedgerClient:
    def __init__(self, node_username: str, database):
        self.node_username = node_username
        self.network_peers = database.get_network_peers(socket.gethostbyname('localhost'))
        print(self.network_peers)

    def broadcast_ledger_change(self, new_block: TransactionBlock):
        for peer in self.network_peers:
            try:
                address = peer[0]
                # Create a new socket for each connection
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # Connect to peer address
                    s.connect((address, PORT))
                    # Send node's info
                    s.send(self.node_username.encode(DATA_FORMAT))
                    # Send new block
                    if new_block:
                        block_data = bytes(str(new_block), DATA_FORMAT)
                        block_length = len(block_data)
                        # Send the length of the block data
                        s.send(f"{block_length:<{HEADER_SIZE}}".encode(DATA_FORMAT))
                        # Send the actual block data
                        s.send(block_data)
            except OSError as os_error:
                # Connection to this server cannot be established.
                pass
