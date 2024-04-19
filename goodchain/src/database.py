import sqlite3
from typing import List
from transaction_block import TransactionBlock

path = "../data/database.db"

class Database:
    """ Perform queries on the node database """
    def __init__(self):
        self.database = '../data/database.db'
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        self.initialize_database()

    def handle_connection(func):
        def wrapper(self, *args, **kwargs):
            # Execute function
            result = func(self, *args, **kwargs)
            # Commit changes and close connection
            self.connection.commit()
            return result
        return wrapper

    @handle_connection
    def initialize_database(self):
        # Ensure Node table exists
        self.cursor.execute(
            """ CREATE TABLE IF NOT EXISTS Node (
                Username text,
                PasswordHash text,
                PublicKey text,
                PrivateKey text
            )"""
        )

    @handle_connection
    def insert_node(self, node: TransactionBlock):
        """ Inserts a node into the database """
        node_dict = {
            'username': node.username,
            'password_hash': node.password_hash,
            'public_key': node.public_key,
            'private_key': node.private_key
        }
        self.cursor.execute(
            """ INSERT INTO Node 
                VALUES (:username, :password_hash, :public_key, :private_key)
                """, node_dict)

    @handle_connection
    def get_node_by_username(self, username: str):
        """ Returns a node by username """
        self.cursor.execute("SELECT * FROM Node WHERE Username = :username", {'username': username})
        return self.cursor.fetchone()

    @handle_connection
    def get_node_username_by_public_key(self, public_key: str):
        """ Returns a node by username """
        self.cursor.execute("SELECT Username FROM Node WHERE PublicKey = :publicKey", {'publicKey': public_key})
        return self.cursor.fetchone()[0]
