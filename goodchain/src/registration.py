""" Registrate a new node """


# Imports
import re
from database import insert_node, get_node_by_username


minimum_amount_of_password_characters = 14


# Functions
def registrate_user():
    node = create_node()
    insert_node(node)
    # TODO: Give node a registration reward


def create_node():
    """" Returns a node object based on user input """
    from node import Node
    # Get node username
    username = input(" Enter a username -> ").strip()

    if not validate_username(username):
        # Let user try to sign up once again
        print("")
        return create_node()

    # Get node password
    password = input(" Enter a password -> ").strip()

    if not validate_password(password):
        # Let user try to sign up once again
        print("")
        return create_node()

    input("Are you sure you want to proceed signing up with the information above?\n"
          "Press enter if you wish to proceed, or else exit the application to abort.")

    # Get hash value of password to store to avoid storing the actual password in our database
    password_hash = get_password_hash_value(password)

    # Create and return node
    return Node(username, password_hash)


def get_password_hash_value(password):
    import hashlib
    digest = hashlib.sha256()
    digest.update(password.encode())
    return digest.hexdigest()


def validate_username(username):
    """ Validates a username """
    # Empty check
    if not username:
        print("Username cannot be empty.")
        return False

    # Duplicate check
    if get_node_by_username(username) is not None:
        print("Username already exists.")
        return False

    return True


def validate_password(password):
    """ Validates a password on behalf of GoodChain's password policy """
    # Empty check
    if not password:
        print("Password cannot be empty.")

    # Type check
    if not isinstance(password, str):
        print("Password must contain letters as well.")
        return False

    # Length check
    if len(password) < minimum_amount_of_password_characters:
        print(f"Password must be at least {minimum_amount_of_password_characters} characters long.")
        return False

    # Uppercase check
    if not re.search("[A-Z]", password):
        print("Password must contain at least one uppercase letter.")
        return False
    # Lowercase check
    elif not re.search("[a-z]", password):
        print("Password must contain at least one lowercase letter.")

    # Digit check
    if not re.search("[0-9]", password):
        print("Password must contain at least one digit.")
        return False

    # Special character check
    if not re.search("[!@#$%^&*()]", password):
        print("Password must contain at least one special character: (!@#$%^&*()).")
        return False

    return True
