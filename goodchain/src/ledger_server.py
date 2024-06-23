from ledger import Ledger
from server import Server, CRUD


class LedgerServer(Server):
    default_port = 6060

    def __init__(self, port=default_port):
        super().__init__(port)
        self.server_data_file_path = "../data/ledger_servers.dat"

    def handle_client(self, connection):
        data = self.get_client_data(connection)
        crud_operation = data[0]
        if crud_operation == CRUD.get("ADD"):
            # Add new block to ledger
            new_block = data[1]
            if new_block.block_hash:
                Ledger.add_block(new_block)
        elif crud_operation == CRUD.get("UPDATE"):
            # Update ledger
            updated_block = data[1]
            Ledger.update_block(updated_block)
        elif crud_operation == CRUD.get("DELETE"):
            # Remove block on ledger
            obsolete_block = data[1]
            Ledger.remove_block(obsolete_block)
        elif crud_operation == CRUD.get("REGISTER"):
            # Add new server to network
            new_server = data[1]
            self.add_server(new_server)
