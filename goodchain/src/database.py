import os
from socket import gethostbyname
import sqlite3


path = "../data/database.db"


class Database:
    """ Perform queries on the node database """
    def __init__(self):
        self.database = '../data/database.db'
        os.makedirs(os.path.dirname(self.database), exist_ok=True)
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        self.initialize_database()
        self.add_user_ip_address()

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
                LastLogin DATETIME
            )"""
        )
        # Ensure User table exists
        self.cursor.execute(
            """ CREATE TABLE IF NOT EXISTS User (
                Address text
            )"""
        )

    @handle_connection
    def add_user_ip_address(self):
        """ Adds the user's ip address if it doesn't exist already """
        # Get your IP address
        address = gethostbyname('localhost')
        # Check if it already is in the db
        self.cursor.execute("SELECT Address FROM User WHERE Address = address", {'address': address})
        is_known_ip_address = self.cursor.fetchone() is not None
        if not is_known_ip_address:
            self.cursor.execute("INSERT INTO User (Address) VALUES (?)", (address,))

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
            return node[-1]
        else:
            return None

    @handle_connection
    def update_last_login_date(self, username: str):
        """ Updates the last login date for a node """
        self.cursor.execute(
            """ UPDATE Node 
                SET LastLogin = CURRENT_TIMESTAMP
                WHERE Username = :username
                """, {'username': username})
