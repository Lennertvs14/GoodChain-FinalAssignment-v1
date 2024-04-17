from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from ledger import Ledger
from transaction import Transaction, REWARD
from transaction_pool import TransactionPool
from transaction_block import TransactionBlock
from user_interface import UserInterface
from wallet import Wallet


minimum_transactions = 5


class Node:
    """ A Node represents a registered user. """
    ui = UserInterface()

    def __init__(self, username, password_hash, public_key=None, private_key=None):
        self.username = username
        self.password_hash = password_hash
        if public_key and private_key:
            self.public_key = public_key
            self.private_key = private_key
        else:
            self.private_key, self.public_key = self.__generate_serialized_keys()

    def show_menu(self):
        """ Shows the private menu """
        print(f"Welcome {self.username}\n")
        print(
            "1 - Profile\n"
            "2 - Explore the blockchain\n"
            "3 - Send coins\n"
            "4 - Explore the transaction pool\n"
            "5 - Mine\n"
            "6 - Show transaction history\n"
            "7 - Log out\n"
        )

    def handle_menu_user_input(self):
        """ Handles user input for the private menu interface """
        chosen_menu_item = input("-> ")
        try:
            chosen_menu_item = int(chosen_menu_item)
            match chosen_menu_item:
                case 1:
                    self.ui.clear_console()
                    print("Profile")
                    self.show_profile()
                case 2:
                    self.ui.clear_console()
                    print("Explore the blockchain")
                    Ledger.show_ledger()
                case 3:
                    self.ui.clear_console()
                    print("Send Coins")
                    self.send_coins()
                case 4:
                    self.ui.clear_console()
                    print("Explore the transaction pool")
                    TransactionPool.show_transaction_pool()
                case 5:
                    self.ui.clear_console()
                    print("Mine")
                    self.mine()
                case 6:
                    self.ui.clear_console()
                    print("Transaction history")
                    print(self.wallet.transactions)
                case 7:
                    self.ui.clear_console()
                    print("You're logged out, thanks for using GoodChain!")
                    return None
                case _:
                    raise ValueError("Invalid choice.")
        except ValueError:
            print("Enter valid digits only.")
        return self

    def grant_reward(self, amount: float):
        """ Grants a reward by a transaction """
        reward_transaction = Transaction(transaction_type=REWARD)
        reward_transaction.add_output(self.public_key, amount)
        TransactionPool.add_transaction(reward_transaction)

    def show_profile(self):
        """ Prints profile (username, public key and private key) """
        print(f"Username: {self.username}\n")
        print("Public key: ")
        print(fr"{str(self.public_key, encoding='utf-8')}")
        print("Private key: ")
        print(fr"{str(self.private_key, encoding='utf-8')}")


    def send_coins(self):
        """ Creates a transaction for a coin transfer to a given node (chosen by username) """
        print("Enter the exact username of the node you would like to transfer coins to.")
        recipient = self.__get_recipient_node_by_username()

        print(f"\nEnter the exact amount of coins you would like to transfer to {recipient[0]}.")
        withdrawal_amount = self.__get_transfer_amount()

        print("\nEnter the exact amount of transaction fee.")
        transaction_fee = self.__get_transfer_amount()

        # Create transaction
        transaction = Transaction(transaction_fee=transaction_fee)
        transaction.add_input(self.public_key, withdrawal_amount+transaction_fee)
        transaction.add_output(recipient[2], withdrawal_amount)

        # Get confirmation
        print(f"\nAre you sure you want to proceed with the following transaction:"
              f"\n{transaction}")
        input(f"\nPress enter if you wish to proceed, or else exit the application to abort.")

        transaction.sign(self.private_key)
        TransactionPool.add_transaction(transaction)

    def __get_recipient_node_by_username(self):
        """ Returns a node chosen by the user to send coins to """
        recipient_username = input("Username -> ").strip()
        recipient_node = get_node_by_username(recipient_username)
        if recipient_node and recipient_node[0] != self.username:
            return recipient_node
        else:
            print(f"No node with this username could be found, please try again.")
            return self.__get_recipient_node_by_username()

    def __get_transfer_amount(self):
        """
        Prompts the user to specify the amount of coins to transfer.
        Returns the amount of coins the user would like to transfer.
        """
        amount = input("Amount -> ").strip()
        try:
            float_value = float(amount.replace(',', '.'))
            return float_value
        except ValueError:
            print(f"This is not an acceptable amount, please try again.")
            return self.__get_transfer_amount()

    def __generate_serialized_keys(self):
        """ Returns a serialized cryptographic private- and public key object """
        # Generate keys
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        # Serialize keys
        serialized_private_key = private_key.private_bytes(
           encoding=serialization.Encoding.PEM,
           format=serialization.PrivateFormat.TraditionalOpenSSL,
           encryption_algorithm=serialization.NoEncryption()
        )
        serialized_public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return serialized_private_key, serialized_public_key
