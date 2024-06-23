from database import Database
from server import Server, CRUD


class NodeServer(Server):
    database = Database()

    def __init__(self, port=5050):
        super().__init__(port)
        self.server_data_file_path = "../data/database_servers.dat"

    def handle_client(self, connection):
        data = self.get_client_data(connection)
        crud_operation = data[0]
        if crud_operation == CRUD.get("ADD"):
            new_node = data[1]
            if new_node:
                self.database.insert_node(new_node)
        elif crud_operation == CRUD.get("UPDATE"):
            updated_node = data[1]
            if updated_node:
                self.database.update_last_login(updated_node.username, updated_node.is_logged_in)
        elif crud_operation == CRUD.get("REGISTER"):
            new_server = data[1]
            self.add_server(new_server)
