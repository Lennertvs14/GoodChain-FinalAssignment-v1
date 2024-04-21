from block import block_status
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from ledger import Ledger
from system import System
from transaction import Transaction
from transaction_pool import TransactionPool
from transaction_block import TransactionBlock
from user_interface import UserInterface, whitespace
from wallet import Wallet
from database import Database


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
        self.wallet = Wallet(self)
        self.validate_last_block()

    def validate_last_block(self):
        """ Validates the last block in the ledger if applicable """
        last_block = Ledger.get_last_block()

        verified_block_status = block_status.get("VERIFIED")
        if not last_block or last_block.status == verified_block_status or last_block.miner.username == self.username:
            return

        if last_block.is_valid():
            last_block.valid_flags += 1
        else:
            last_block.invalid_flags += 1

        if last_block.valid_flags == 3:
            last_block.status = verified_block_status
            miners_reward = 50.0
            System.grant_reward(last_block.miner, (miners_reward+last_block.total_transaction_fee))
        elif last_block.invalid_flags == 3:
            # Return transactions to pool
            for transaction in last_block.data:
                TransactionPool.add_transaction(transaction)
            # Remove block from ledger
            Ledger.remove_block(last_block)

        last_block.validated_by.append(self.username)
        Ledger.update_block(last_block)

    def show_menu(self):
        """ Shows the private menu """
        print(f"Welcome {self.username}\n")
        print(
            "1 - Profile\n"
            "2 - Explore the blockchain\n"
            "3 - Check balance\n"
            "4 - Send coins\n"
            "5 - Explore the transaction pool\n"
            "6 - Mine\n"
            "7 - Validate block(s)\n"
            "8 - Show transaction history\n"
            "9 - Log out\n"
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
                    print("Check balance")
                    print(self.wallet.available_balance)
                case 4:
                    self.ui.clear_console()
                    print("Send Coins")
                    self.send_coins()
                case 5:
                    self.ui.clear_console()
                    print("Explore the transaction pool")
                    TransactionPool.show_transaction_pool()
                case 6:
                    self.ui.clear_console()
                    print("Mine")
                    self.mine()
                case 7:
                    self.ui.clear_console()
                    print("Validate block(s)")
                    self.mine()
                case 8:
                    self.ui.clear_console()
                    print("Transaction history")
                    print(self.wallet.transactions)
                case 9:
                    self.ui.clear_console()
                    print("You're logged out, thanks for using GoodChain!")
                    return None
                case _:
                    raise ValueError("Invalid choice.")
        except ValueError:
            print("Enter valid digits only.")
        return self

    def show_profile(self):
        """ Prints profile (username, public key and private key) """
        print(f"Username: {self.username}\n")
        print("Public key: ")
        print(fr"{str(self.public_key, encoding='utf-8')}")
        print("Private key: ")
        print(fr"{str(self.private_key, encoding='utf-8')}")

    def mine(self):
        """ Mines a block if that's possible """
        # Get data
        transaction_pool = TransactionPool.get_transactions()
        blocks = Ledger.get_blocks()

        is_genesis_block = blocks is None or len(blocks) < 1

        if not self.__validate_mining_conditions(transaction_pool, is_genesis_block):
            return

        # Get max amount of transactions
        maximum_transactions = 10
        if len(transaction_pool) < maximum_transactions:
            # You cannot mine more than the available amount of transactions even if you wanted to
            maximum_transactions = len(transaction_pool)

        chosen_transactions = self.__get_transactions_to_mine(maximum_transactions)

        # Get confirmation
        input("Press enter if you wish to proceed.")
        try:
            valid_transactions = []
            invalid_transactions = []

            for i, transaction in enumerate(chosen_transactions):
                if transaction.is_valid():
                    transaction.valid = True
                    valid_transactions.append(transaction)
                else:
                    invalid_transactions.append(transaction)

            if not self.__validate_mining_conditions(valid_transactions, True):
                return

            if is_genesis_block:
                new_block = TransactionBlock(None)
            else:
                new_block = TransactionBlock(Ledger.get_last_block())

            total_transaction_fee = 0.0
            for valid_transaction in valid_transactions:
                total_transaction_fee += valid_transaction.transaction_fee
                new_block.add_transaction(valid_transaction)

            leading_zeros = 2
            new_block.mine(leading_zeros)
            new_block.miner = self

            # Add new block to ledger
            Ledger.add_block(new_block)

            print("\nCongrats, expect your reward soon!")

            if new_block.is_valid():
                # Remove valid transactions from pool
                TransactionPool.remove_transactions(valid_transactions)

            if len(invalid_transactions) > 0:
                TransactionPool.flag_invalid_transactions(invalid_transactions)
        except:
            print("Something went wrong, please try again.")

    def send_coins(self):
        """ Creates a transaction for a coin transfer to a given node (chosen by username) """
        print("Enter the exact username of the node you would like to transfer coins to.")
        recipient = self.__get_recipient_node_by_username()

        print(f"\nEnter the exact amount of coins you would like to transfer to {recipient[0]}.")
        withdrawal_amount = self.__get_transfer_amount()

        print("\nEnter the exact amount of transaction fee.")
        transaction_fee = self.__get_transfer_amount()

        # Balance validation
        total_input = withdrawal_amount+transaction_fee
        if self.wallet.available_balance < total_input:
            print("You do not have enough balance, please try again later.")
            return

        # Create transaction
        transaction = Transaction(transaction_fee=transaction_fee)
        transaction.add_input(self.public_key, total_input)
        transaction.add_output(recipient[2], withdrawal_amount)

        # Get confirmation
        print(f"\nAre you sure you want to proceed with the following transaction:"
              f"\n{transaction}")
        input(f"\nPress enter if you wish to proceed.")

        transaction.sign(self.private_key)
        if transaction.is_valid():
            TransactionPool.add_transaction(transaction)
            print("Your transfer is successfully initialised!")
        else:
            print("Your transaction is invalid, please try again.")

    def __validate_mining_conditions(self, transaction_pool, is_genesis_block):
        """ Validates if GoodChain's mining conditions are met """
        # Transaction pool validation
        if 0 < len(transaction_pool) < minimum_transactions:
            print(f"There are not enough transactions in the transaction pool, "
                  f"there must be at least {minimum_transactions} transactions.")
            return False

        # Time interval validation
        if not is_genesis_block:
            last_block = Ledger.get_last_block()
            last_block_creation_date = last_block.creation_date
            current_time = datetime.now()
            time_difference = current_time - last_block_creation_date
            required_time_difference_in_minutes = 3
            if time_difference < timedelta(minutes=required_time_difference_in_minutes):
                print(f"It has not been {required_time_difference_in_minutes} minutes since the last block's creation.")
                return False
            # Last block validation
            verified_block_status = block_status.get("VERIFIED")
            if last_block.status != verified_block_status:
                print(f"You can not mine a new block until its considered valid.")
                return False

        # All checks passed
        return True

    def __get_transactions_to_mine(self, maximum_transactions, show_transactions=True):
        """ Returns the transactions the user is allowed to mine """
        chosen_transactions = []
        # Prioritize reward transactions
        reward_transactions = TransactionPool.get_reward_transactions()
        required_transactions = 0
        if len(reward_transactions) > 0:
            print("You are required to mine at least the following reward transaction(s).")
            for transaction in reward_transactions:
                if required_transactions > maximum_transactions:
                    break
                print(whitespace + f"{transaction}")
                chosen_transactions.append(transaction)
                required_transactions += 1
        # See if the user is still able to custom pick transactions
        transactions_to_chose = maximum_transactions-required_transactions
        print(f"You are allowed to choose {transactions_to_chose} transaction(s) your self.")
        # Let a user chose transactions if applicable
        if transactions_to_chose > 0:
            # Show available transactions to choose from
            if show_transactions and transactions_to_chose > 0:
                TransactionPool.show_transaction_pool(with_reward_transactions=False, with_invalid_transactions=False)
            # Get available transactions to choose from
            available_transactions = TransactionPool.get_transactions(with_reward_transactions=False)
            # Handle user input
            print("Enter the identities of the transactions you'd like to mine one for one.")
            print(f"Note: the loop will stop soon as you reach {transactions_to_chose} distinct transactions "
                  f"or if you write 'done'.")
            transaction_identities = []
            while len(chosen_transactions) < maximum_transactions:
                transaction_id = input("ID -> ").strip()
                try:
                    transaction_id = int(transaction_id)
                    if transaction_id in transaction_identities:
                        print("You have chosen this transaction already, please try another one.")
                    elif 0 < transaction_id <= len(available_transactions):
                        transaction_identities.append(transaction_id)
                        transaction_index = transaction_id - 1
                        chosen_transactions.append(available_transactions[transaction_index])
                    else:
                        print("Invalid id, please try again.")
                except ValueError:
                    if transaction_id.lower() == "done":
                        if len(chosen_transactions) > minimum_transactions:
                            break
                        else:
                            print(f"You must chose at least {minimum_transactions-len(chosen_transactions)} "
                                  f"transaction(s) more.")
                    else:
                        print("Invalid id, please try again.")
        return chosen_transactions

    def __get_recipient_node_by_username(self):
        """ Returns a node chosen by the user to send coins to """
        database = Database()
        recipient_username = input("Username -> ").strip()
        recipient_node = database.get_node_by_username(recipient_username)
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
