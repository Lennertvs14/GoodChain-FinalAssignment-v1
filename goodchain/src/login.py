""" Handle the user login process """


# Imports
from node import Node
from database import get_node_by_username
import hashlib


# Functions
def login():
    """" Returns a node upon a successful login attempt """
    # Get necessary user input
    username = input(" Enter a username -> ")
    password = input(" Enter a password -> ")

    # Assert username
    node_entity = get_node_by_username(username)
    if node_entity:
        # Assert passwords
        entered_password_hash = get_password_hash_value(password)
        expected_password_hash = node_entity[1]
        if entered_password_hash == expected_password_hash:
            # Login attempt successful, now return the corresponding node object
            return create_node_from_entity(node_entity)

    # Login attempt unsuccessful
    print("Failed to login, check your input and try again.\n")
    return login()


def get_password_hash_value(password):
    digest = hashlib.sha256()
    digest.update(password.encode())
    return digest.hexdigest()


def create_node_from_entity(node_entity):
    """ Create a Node object from a node entity """
    return Node(node_entity[0], node_entity[1], node_entity[2], node_entity[3])