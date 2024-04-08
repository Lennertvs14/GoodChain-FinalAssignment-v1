""" Perform queries on the node database """

import sqlite3


def connect_to_database(func):
    def wrapper(*args, **kwargs):
        # Open connection
        database = '../data/database.db'
        connection = sqlite3.connect(database)
        # Ensure Node table exists
        cursor = connection.cursor()
        cursor.execute(
            """ CREATE TABLE IF NOT EXISTS Node (
                Username text,
                PasswordHash text,
                PublicKey text,
                PrivateKey text
            )"""
        )
        connection.commit()
        # Execute function
        result = func(connection, cursor, *args, **kwargs)
        # Close connection
        connection.close()
        return result
    return wrapper


@connect_to_database
def insert_node(connection, cursor, node):
    """ Inserts a node into the database """
    node_dict = {
        'username': node.username,
        'password_hash': node.password_hash,
        'public_key': node.public_key,
        'private_key': node.private_key
    }
    with connection:
        cursor.execute(
            """ INSERT INTO Node 
                VALUES (:username, :password_hash, :public_key, :private_key)
                """, node_dict)


@connect_to_database
def get_node_by_username(connection, cursor, username):
    """ Returns a node by username """
    cursor.execute("SELECT * FROM Node WHERE Username = :username", {'username': username})
    return cursor.fetchone()
