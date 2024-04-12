from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from database import get_node_by_username
from transaction import Transaction
import transaction_pool


class Node:
    """ A Node represents a registered user. """

    def __init__(self, username, password_hash, public_key=None, private_key=None):
        self.username = username
        self.password_hash = password_hash
        if public_key and private_key:
            self.public_key = public_key
            self.private_key = private_key
        else:
            self.private_key, self.public_key = self.__generate_serialized_keys()

    def send_coins(self):
        """ Creates a transaction for a coin transfer to a given node (chosen by username) """
        print("Enter the exact username of the node you would like to transfer coins to.")
        recipient = self.__get_recipient_node_by_username()

        print(f"\nEnter the exact amount of coins you would like to transfer to {recipient[0]}.")
        withdrawal_amount = self.__get_transfer_amount()

        print("\nEnter the exact amount of transaction fee.")
        transaction_fee = self.__get_transfer_amount()

        transaction = Transaction(transaction_fee=transaction_fee)
        transaction.add_input(self.public_key, withdrawal_amount+transaction_fee)
        transaction.add_output(recipient[2], withdrawal_amount)

        # Get confirmation
        print(f"\nAre you sure you want to proceed with the following transaction:"
              f"\n{transaction}")
        input(f"\nPress enter if you wish to proceed, or else exit the application to abort.")

        transaction.sign(self.private_key)
        transaction_pool.add_transaction(transaction)
        print("LOLOLOL!")

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
