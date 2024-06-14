from database import Database
from ledger import Ledger
from ledger_server import LedgerServer
from node import Node
import re
from system import System
from user_interface import UserInterface


class User:
    """ Represents a user that is not logged in """
    ui = UserInterface()

    @staticmethod
    def get_password_hash_value(password):
        """ Returns the hash value for a given password """
        import hashlib
        digest = hashlib.sha256()
        digest.update(password.encode())
        return digest.hexdigest()

    @staticmethod
    def show_menu():
        """ Shows the public menu (meant for users that aren't logged in) """
        print("GoodChain Public Menu\n")
        print(
            "1 - Login\n"
            "2 - Explore the blockchain\n"
            "3 - Sign up\n"
            "4 - Exit\n"
        )

    def __init__(self):
        self.database = Database()

        self.ledger_server = LedgerServer()
        self.ledger_server.start_server()
        self.database.insert_ledger_server_port(self.ledger_server.port)

    def handle_menu_user_input(self):
        """ Handles user input for the public menu interface """
        chosen_menu_item = input("-> ")
        try:
            chosen_menu_item = int(chosen_menu_item)
            match chosen_menu_item:
                case 1:
                    self.ui.clear_console()
                    print("Login")
                    return self.login()
                case 2:
                    self.ui.clear_console()
                    Ledger.show_menu()
                    Ledger.handle_menu_input()
                    input("Press enter to continue.")
                case 3:
                    self.ui.clear_console()
                    print("Sign up")
                    self.registrate()
                case 4:
                    self.ledger_server.stop_server()
                    self.database.remove_ledger_server_port(self.ledger_server.port)
                    System().exit()
                case _:
                    raise ValueError("Invalid choice.")
        except ValueError:
            print("Enter digits only.")

    def registrate(self):
        """ Registrates a new node """
        print("Write 'back' to go back.")
        node = self.__create_node()
        if node is None:
            return
        self.database.insert_node(node)
        sign_up_reward = 50.0
        System.grant_reward(node, sign_up_reward)

    def login(self):
        """" Returns a node upon a successful login attempt """
        attempts = 1
        max_amount_of_attempts = 4
        while attempts < max_amount_of_attempts:
            # Get necessary user input
            username = input(" Enter a username -> ").strip()
            password = input(" Enter a password -> ").strip()

            # Assert username
            node_entity = self.database.get_node_by_username(username)
            if node_entity:
                # Assert passwords
                entered_password_hash = self.get_password_hash_value(password)
                expected_password_hash = node_entity[1]
                if entered_password_hash == expected_password_hash:
                    # Login attempt successful, now return the corresponding node object
                    return self.__convert_node_entity_to_instance(node_entity)

            # Login attempt unsuccessful
            remaining_attempts = (max_amount_of_attempts - attempts) - 1
            print(f"Failed to login, you have {remaining_attempts} attempt(s) left.\n")
            attempts += 1

        # User tried too many times
        System().exit()

    def __convert_node_entity_to_instance(self, node_entity):
        """ Create a Node instance from a node entity """
        return (
            Node(node_entity[0], node_entity[1], self.ledger_server, node_entity[2], node_entity[3], True)
        )

    def __create_node(self):
        """" Returns a node object based on user input """
        # Get node username
        username = input("Enter a username -> ").strip()
        if username == 'back':
            return None
        elif not self.__validate_username(username):
            # Let user try to sign up once again
            print("")
            return self.__create_node()

        # Get node password
        password = input("Enter a password -> ").strip()
        if password == 'back':
            return None
        elif not self.__validate_password(password):
            # Let user try to sign up once again
            print("")
            return self.__create_node()

        input("Are you sure you want to proceed signing up with the information above?\n"
              "Press enter if you wish to proceed, otherwise exit the app.")

        # Get hash value of password to store to avoid storing the actual password in our database
        password_hash = self.get_password_hash_value(password)

        # Create and return node
        return Node(username, password_hash, self.ledger_server)

    def __validate_username(self, username):
        # Empty check
        if not username:
            print("[FAILED] Username cannot be empty.")
            return False

        # Duplicate check
        if self.database.get_node_by_username(username) is not None:
            print("[FAILED] Username already exists.")
            return False

        return True

    def __validate_password(self, password):
        minimum_amount_of_password_characters = 14

        # Empty check
        if not password:
            print("[FAILED] Password cannot be empty.")

        # Type check
        if not isinstance(password, str):
            print("[FAILED] Password must contain letters as well.")
            return False

        # Length check
        if len(password) < minimum_amount_of_password_characters:
            print(f"[FAILED] Password must be at least {minimum_amount_of_password_characters} characters long.")
            return False

        # Uppercase check
        if not re.search("[A-Z]", password):
            print("[FAILED] Password must contain at least one uppercase letter.")
            return False
        # Lowercase check
        elif not re.search("[a-z]", password):
            print("[FAILED] Password must contain at least one lowercase letter.")

        # Digit check
        if not re.search("[0-9]", password):
            print("[FAILED] Password must contain at least one digit.")
            return False

        # Special character check
        if not re.search("[!@#$%^&*()]", password):
            print("[FAILED] Password must contain at least one special character: (!@#$%^&*()).")
            return False

        return True
