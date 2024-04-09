""" Handle the user login process """


# Imports
from node import Node
from database import get_node_by_username
import hashlib


# Functions
def login():
    """" Returns a node upon a successful login attempt """
    attempts = 1
    max_amount_of_attempts = 7
    while attempts < max_amount_of_attempts:
        # Get necessary user input
        username = input(" Enter a username -> ").strip()
        password = input(" Enter a password -> ").strip()

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
        remaining_attempts = (max_amount_of_attempts - attempts) - 1
        print(f"Failed to login, you have {remaining_attempts} attempt(s) left.\n")
        attempts += 1


def get_password_hash_value(password):
    digest = hashlib.sha256()
    digest.update(password.encode())
    return digest.hexdigest()


def create_node_from_entity(node_entity):
    """ Create a Node object from a node entity """
    return Node(node_entity[0], node_entity[1], node_entity[2], node_entity[3])