from database import Database
from ledger import Ledger
from ledger_server import LedgerServer
from node import Node
from node_server import NodeServer
import re
from system import System
from transaction_server import TransactionServer
from user_interface import UserInterface, TEXT_COLOR


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
        self.node_server = NodeServer()
        self.node_server.insert_server()
        self.node_server.start_server()
        print(f"Node server listening on {self.node_server.port}")

        self.ledger_server = LedgerServer()
        self.ledger_server.insert_server()
        self.ledger_server.start_server()
        print(f"Ledger server listening on {self.ledger_server.port}")

        self.transaction_server = TransactionServer()
        self.transaction_server.insert_server()
        self.transaction_server.start_server()
        print(f"Transaction server listening on {self.transaction_server.port}")

    def handle_menu_user_input(self):
        """ Handles user input for the public menu interface """
        chosen_menu_item = input("-> ")
        try:
            chosen_menu_item = int(chosen_menu_item)
            match chosen_menu_item:
                case 1:
                    self.ui.clear_console()
                    print(self.ui.format_text("Login", TEXT_COLOR.get("YELLOW")) + "\n")
                    return self.login()
                case 2:
                    self.ui.clear_console()
                    Ledger.show_menu()
                    Ledger.handle_menu_input()
                    input("\n" + self.ui.PRESS_ENTER_TO_CONTINUE)
                case 3:
                    self.ui.clear_console()
                    print(self.ui.format_text("Sign up", TEXT_COLOR.get("YELLOW")) + "\n")
                    self.registrate()
                case 4:
                    self.ledger_server.stop_server()
                    System().exit()
                case _:
                    print(self.ui.INVALID_MENU_ITEM)
                    input("\nPress enter to continue.")
        except ValueError:
            print(self.ui.ENTER_DIGITS_ONLY)
            input("\nPress enter to continue.")

    def registrate(self):
        """ Registrates a new node """
        from server import CRUD
        print("Write " + self.ui.BACK + " to go back.")
        node = self.__create_node()
        if node:
            self.database.insert_node(node)
            sign_up_reward = 50.0
            reward_transaction = System.grant_reward(node, sign_up_reward)
            node.node_client.broadcast_change(CRUD.get("ADD"), node)
            node.transaction_client.broadcast_change(CRUD.get("ADD"), [reward_transaction])

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
                    # Login attempt successful
                    node_account_is_available = self.database.is_node_logged_in(username) == 0
                    if node_account_is_available:
                        # Return the corresponding node object
                        return self.__convert_node_entity_to_instance(node_entity)
                    else:
                        error_text = "Failed to login, there is someone logged in on this account already."
                        print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
                        input("\n" + self.ui.PRESS_ENTER_TO_CONTINUE)
                        return

            # Login attempt unsuccessful
            remaining_attempts = (max_amount_of_attempts - attempts) - 1
            error_text = f"Failed to login, you have {remaining_attempts} attempt(s) left.\n"
            print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
            attempts += 1

        # User tried too many times
        System().exit()

    def __convert_node_entity_to_instance(self, node_entity):
        """ Create a Node instance from a node entity """
        return (
            Node(self, node_entity[0], node_entity[1], (node_entity[2], node_entity[3]), True)
        )

    def __create_node(self):
        """" Returns a node object based on user input """
        # Get node username
        username = input("Enter a username " + self.ui.INPUT_ARROW).strip()
        if username == 'back':
            return None
        elif not self.__validate_username(username):
            # Let user try to sign up once again
            print("")
            return self.__create_node()

        # Get node password
        password = input("Enter a password " + self.ui.INPUT_ARROW).strip()
        if password == 'back':
            return None
        elif not self.__validate_password(password):
            # Let user try to sign up once again
            print("")
            return self.__create_node()

        print("Are you sure you want to proceed signing up with the information above?")
        input(self.ui.PRESS_ENTER_TO_CONTINUE)

        # Get hash value of password to store to avoid storing the actual password in our database
        password_hash = self.get_password_hash_value(password)

        # Create and return node
        return Node(self, username, password_hash)

    def __validate_username(self, username):
        # Empty check
        if not username:
            print(self.ui.format_text("Username cannot be empty.", TEXT_COLOR.get("RED")))
            return False

        # Duplicate check
        if self.database.get_node_by_username(username) is not None:
            print(self.ui.format_text("Username already exists.", TEXT_COLOR.get("RED")))
            return False

        return True

    def __validate_password(self, password):
        minimum_amount_of_password_characters = 14

        # Empty check
        if not password:
            print(self.ui.format_text("Password cannot be empty.", TEXT_COLOR.get("RED")))

        # Type check
        if not isinstance(password, str):
            error_text = "Password must contain letters as well."
            print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
            return False

        # Length check
        if len(password) < minimum_amount_of_password_characters:
            error_text = f"Password must be at least {minimum_amount_of_password_characters} characters long."
            print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
            return False

        # Uppercase check
        if not re.search("[A-Z]", password):
            error_text = "Password must contain at least one uppercase letter."
            print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
            return False
        # Lowercase check
        elif not re.search("[a-z]", password):
            error_text = "Password must contain at least one lowercase letter."
            print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))

        # Digit check
        if not re.search("[0-9]", password):
            print(self.ui.format_text("Password must contain at least one digit.", TEXT_COLOR.get("RED")))
            return False

        # Special character check
        if not re.search("[!@#$%^&*()]", password):
            error_text = "Password must contain at least one special character: (!@#$%^&*())."
            print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
            return False

        return True
