from transaction_pool import TransactionPool
from server import Server, CRUD


class TransactionServer(Server):
    default_port = 7070

    def __init__(self, port=default_port):
        super().__init__(port)
        self.server_data_file_path = "../data/transaction_servers.dat"

    def handle_client(self, connection):
        data = self.get_client_data(connection)
        crud_operation = data[0]
        if crud_operation == CRUD.get("ADD"):
            new_transactions = data[1]
            for new_transaction in new_transactions:
                TransactionPool.add_transaction(new_transaction)
        elif crud_operation == CRUD.get("UPDATE"):
            updated_transaction = data[1]
            TransactionPool.update_transactions(updated_transaction)
        elif crud_operation == CRUD.get("DELETE"):
            obsolete_transactions = data[1]
            TransactionPool.remove_transactions(obsolete_transactions)
        elif crud_operation == CRUD.get("REGISTER"):
            new_server = data[1]
            self.add_server(new_server)
