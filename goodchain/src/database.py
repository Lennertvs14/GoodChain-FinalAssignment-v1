import os
import sqlite3


PATH = "../data/database.db"


class Database:
    """ Perform queries on the node database """
    def __init__(self):
        os.makedirs(os.path.dirname(PATH), exist_ok=True)
        self.connection = sqlite3.connect(PATH, check_same_thread=False)
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
                PrivateKey text,
                LastLogin DATETIME,
                IsLoggedIn BOOLEAN DEFAULT 0
            )"""
        )

    @handle_connection
    def insert_node(self, node):
        """ Inserts a node into the database """
        node_dict = {
            'username': node.username,
            'password_hash': node.password_hash,
            'public_key': node.public_key,
            'private_key': node.private_key
        }
        self.cursor.execute(
            """ INSERT INTO Node (Username, PasswordHash, PublicKey, PrivateKey)
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

    @handle_connection
    def get_last_login_date(self, username: str):
        """ Returns the last time a node logged in """
        node = self.get_node_by_username(username)
        if node:
            # LastLogin extraction from node dict
            return node[-2]
        else:
            return None

    @handle_connection
    def update_last_login_date(self, username: str):
        """ Updates the last login date for a node """
        self.cursor.execute(
            """ UPDATE Node 
                SET LastLogin = CURRENT_TIMESTAMP,
                    IsLoggedIn = 1
                WHERE Username = :username
                """, {'username': username})

    @handle_connection
    def log_out_node(self, username: str):
        """ Updates the IsLoggedIn boolean for a node """
        self.cursor.execute(
            """ UPDATE Node
            SET IsLoggedIn = 0
            WHERE Username = :username
            """, {'username': username}
        )

    @handle_connection
    def is_node_logged_in(self, username: str):
        """ Returns whether the node is logged in or not """
        self.cursor.execute(
            """ SELECT IsLoggedIn
            FROM Node
            WHERE Username = :username
            """, {'username': username}
        )
        return (self.cursor.fetchone())[0]
