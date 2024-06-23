from block import block_status
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from database import Database
from datetime import datetime, timedelta
from ledger import Ledger
from ledger_client import LedgerClient
from ledger_server import CRUD
from node_client import NodeClient
from system import System
from transaction import Transaction, REWARD
from transaction_block import TransactionBlock
from transaction_client import TransactionClient
from transaction_pool import TransactionPool
from user_interface import UserInterface, WHITESPACE, TEXT_COLOR
from wallet import Wallet


MINIMUM_TRANSACTIONS = 5
VERIFIED_BLOCK_STATUS = block_status.get("VERIFIED")


class Node:
    """ A Node represents a registered user. """
    ui = UserInterface()
    database = Database()

    def __init__(self, user, username, password_hash, keys: (bytes, bytes) = None, show_notifications=False):
        self.username = username
        self.password_hash = password_hash
        self.is_logged_in = False

        if keys:
            self.public_key = keys[0]
            self.private_key = keys[1]
        else:
            self.private_key, self.public_key = self.__generate_serialized_keys()
        self.wallet = Wallet(self)

        # Map from user
        self.node_server = user.node_server
        self.node_client = NodeClient(self.node_server)
        self.ledger_server = user.ledger_server
        self.ledger_client = LedgerClient(self.ledger_server)
        self.transaction_server = user.transaction_server
        self.transaction_client = TransactionClient(self.transaction_server)

        self.check_last_block()
        if show_notifications:
            self.show_notifications()

    def check_last_block(self):
        """ Checks whether this user must validate the last block """
        last_block = Ledger.get_last_block()

        if not last_block or last_block.status == VERIFIED_BLOCK_STATUS or last_block.miner.username == self.username:
            return

        validators = last_block.validated_by.split()
        if self.username in validators:
            return

        self.verify_block(last_block)

    def verify_block(self, block: TransactionBlock):
        """ Verifies the block by node's username """
        if block.is_valid():
            block.valid_flags += 1
        else:
            block.invalid_flags += 1

        if block.valid_flags == 3:
            block.status = VERIFIED_BLOCK_STATUS
            miners_reward = 50.0
            reward_transaction = System.grant_reward(block.miner, (miners_reward + block.total_transaction_fee))
            self.transaction_client.broadcast_change(CRUD.get("ADD"), [reward_transaction])
        elif block.invalid_flags == 3:
            # Return transactions to pool
            for transaction in block.data:
                TransactionPool.add_transaction(transaction)
                self.transaction_client.broadcast_change(CRUD.get("ADD"), [transaction])
            # Remove block from ledger
            Ledger.remove_block(block)
            self.ledger_client.broadcast_change(CRUD.get("DELETE"), block)
            return

        block.validated_by += " " + self.username
        Ledger.update_block(block)
        self.ledger_client.broadcast_change(CRUD.get("UPDATE"), block)

    def show_notifications(self):
        """ Shows notifications """
        self.ui.clear_console()
        print(f"Welcome {self.username}, here are your notifications:\n")

        # Show amount of mined blocks
        current_blocks = Ledger.get_blocks()
        chain_length = len(current_blocks)
        print(f"GoodChain currently has {chain_length} block(s) in the ledger.")

        # Show status of pending transactions and handle invalid transactions
        transaction_pool = TransactionPool.get_transactions()
        for transaction in transaction_pool:
            if transaction.type != REWARD and transaction.input[0] == self.public_key:
                if transaction.valid is False:
                    print("\nYour following transaction:")
                    print(WHITESPACE + f"{transaction}")
                    print(self.ui.format_text("is considered invalid and has been canceled!", TEXT_COLOR.get("RED")))
                    TransactionPool.remove_transactions([transaction])
                    self.transaction_client.broadcast_change(CRUD.get("DELETE"), [transaction])
                else:
                    print("\nYour following transaction:")
                    print(WHITESPACE + f"{transaction}")
                    print("is still pending for withdrawal.")
            elif transaction.output[0] == self.public_key and transaction.valid is True:
                print("\nThe following transaction:")
                print(WHITESPACE + f"{transaction}")
                print("is pending for arrival.")

        # Get last login date
        last_login_date = self.database.get_last_login_date(self.username)
        if last_login_date is None:
            print("\nThis is your first login!")
        else:
            # Parse the date and time
            last_login_date = datetime.strptime(last_login_date, "%Y-%m-%d %H:%M:%S")
            print(f"\nYour last login was at {last_login_date.date()}.")

        print("\nThese are the new blocks added to our chain:")
        new_blocks = []
        for block in current_blocks:
            if last_login_date is None or block.creation_date > last_login_date:
                new_blocks.append(block)
                print(WHITESPACE + f"#{block.id}")

        # Update last login date
        self.is_logged_in = True
        self.database.update_last_login(self.username, self.is_logged_in)
        self.node_client.broadcast_change(CRUD.get("UPDATE"), self)

        for block in new_blocks:
            if block.miner.username == self.username:
                print(f"\nThe block #{block.id} which you mined is {block.status}")

        for block in new_blocks:
            for transaction in block.data:
                if transaction.type != REWARD and transaction.input[0] == self.public_key:
                    if block.status == block_status.get("VERIFIED"):
                        print("\nYour following transaction:")
                        print(WHITESPACE + f"{transaction}")
                        print("is transferred successfully.")
                    else:
                        print("\nYour following transaction:")
                        print(WHITESPACE + f"{transaction}")
                        print("is still pending for arrival.")
                elif transaction.output[0] == self.public_key:
                    if block.status == block_status.get("VERIFIED"):
                        print("\nYou have received the following transaction:")
                        print(WHITESPACE + f"{transaction}")
                        print("successfully.")
                    else:
                        print("\nThe following transaction:")
                        print(WHITESPACE + f"{transaction}")
                        print("is pending for arrival.")

        input("\n" + self.ui.PRESS_ENTER_TO_CONTINUE)
        return

    def show_menu(self):
        """ Shows the private menu """
        print(self.ui.format_text("Node Menu", TEXT_COLOR.get("YELLOW")) + "\n")
        print(
            "1 - Profile\n"
            "2 - Explore the blockchain\n"
            "3 - Check balance\n"
            "4 - Send coins\n"
            "5 - Cancel transaction\n"
            "6 - Explore the transaction pool\n"
            "7 - Mine\n"
            "8 - Validate block(s)\n"
            "9 - Show transaction history\n"
            "10 - Log out\n"
        )

    def handle_menu_user_input(self):
        """ Handles user input for the private menu interface """
        chosen_menu_item = input(self.ui.INPUT_ARROW)
        try:
            chosen_menu_item = int(chosen_menu_item)
            match chosen_menu_item:
                case 1:
                    self.ui.clear_console()
                    print(self.ui.format_text("Profile", TEXT_COLOR.get("YELLOW")) + "\n")
                    self.show_profile()
                case 2:
                    self.ui.clear_console()
                    Ledger.show_menu()
                    Ledger.handle_menu_input()
                case 3:
                    self.ui.clear_console()
                    print(self.ui.format_text("Check balance", TEXT_COLOR.get("YELLOW")) + "\n")
                    balance = self.wallet.available_balance
                    if balance > 0.0:
                        print(self.ui.format_text(str(balance), TEXT_COLOR.get("GREEN")))
                    else:
                        print(self.ui.format_text(str(balance), TEXT_COLOR.get("RED")))
                case 4:
                    self.ui.clear_console()
                    print(self.ui.format_text("Send Coins", TEXT_COLOR.get("YELLOW")) + "\n")
                    self.send_coins()
                case 5:
                    self.ui.clear_console()
                    print(self.ui.format_text("Cancel a transaction", TEXT_COLOR.get("YELLOW")) + "\n")
                    self.cancel_pending_transaction()
                case 6:
                    self.ui.clear_console()
                    print(self.ui.format_text("Transaction pool", TEXT_COLOR.get("YELLOW")) + "\n")
                    TransactionPool.show_transaction_pool()
                case 7:
                    self.ui.clear_console()
                    print(self.ui.format_text("Mine menu", TEXT_COLOR.get("YELLOW")) + "\n")
                    self.mine()
                case 8:
                    self.ui.clear_console()
                    print(self.ui.format_text("Validate block(s)", TEXT_COLOR.get("YELLOW")) + "\n")
                    self.validate_block()
                case 9:
                    self.ui.clear_console()
                    print(self.ui.format_text("Transaction history", TEXT_COLOR.get("YELLOW")) + "\n")
                    print(self.wallet.transactions)
                case 10:
                    self.log_out()
                    return None
                case _:
                    print(self.ui.INVALID_MENU_ITEM)
        except ValueError:
            print(self.ui.ENTER_DIGITS_ONLY)
        return self

    def show_profile(self):
        """ Prints profile (username, public key and private key) """
        print(f"Username: \n{self.username}\n")
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
        input("\n" + self.ui.PRESS_ENTER_TO_CONTINUE)

        valid_transactions = []
        invalid_transactions = []
        try:
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
            new_block.total_transaction_fee = total_transaction_fee

            if new_block.block_hash:
                # Add new block to ledger
                Ledger.add_block(new_block)
                self.ledger_client.broadcast_change(CRUD.get("ADD"), new_block)

        except Exception as ex:
            print(self.ui.format_text("Something went wrong, please try again.", TEXT_COLOR.get("RED")))

        finally:
            # Remove valid transactions
            TransactionPool.remove_transactions(valid_transactions)
            self.transaction_client.broadcast_change(CRUD.get("DELETE"), valid_transactions)

            # Flag invalid transactions
            if len(invalid_transactions) > 0:
                invalid_transactions = self.__flag_invalid_transactions(invalid_transactions)
                self.transaction_client.broadcast_change(CRUD.get("UPDATE"), invalid_transactions)

            # Wrap up the mining process
            print("\n" + self.ui.format_text("Congrats, expect your reward soon!", TEXT_COLOR.get("GREEN")))

    def validate_block(self):
        """ Validates a block of choice """
        blocks = Ledger.get_blocks()
        Ledger.show_ledger()

        chosen_block_id = input("Enter " + self.ui.BACK + " to go back.\n"
                                "Enter the ID of the block you'd like to validate\n" + self.ui.INPUT_ARROW).strip()
        try:
            chosen_block_id = int(chosen_block_id)
            if 0 <= chosen_block_id < len(blocks):
                chosen_block = blocks[chosen_block_id]

                if chosen_block.miner.username == self.username:
                    print(
                        self.ui.format_text("You cannot validate the block you mined yourself.", TEXT_COLOR.get("RED"))
                    )
                    return

                validators = chosen_block.validated_by.split()
                if self.username in validators:
                    print(self.ui.format_text("You have successfully validated this block.", TEXT_COLOR.get("GREEN")))
                    return

                self.verify_block(chosen_block)
                print(self.ui.format_text("You have successfully validated this block.", TEXT_COLOR.get("GREEN")))
            else:
                print(self.ui.INVALID_ID)
        except ValueError:
            if chosen_block_id == 'back':
                return
            print(self.ui.INVALID_ID)

    def send_coins(self):
        """ Creates a transaction for a coin transfer to a given node (chosen by username) """
        print("Enter the exact username of the node you would like to transfer coins to.")
        recipient = self.__get_recipient_node_by_username()

        if recipient is None:
            return

        print(f"\nEnter the exact amount of coins you would like to transfer to {recipient[0]}.")
        withdrawal_amount = self.__get_transfer_amount()

        if withdrawal_amount is None:
            return

        print("\nEnter the exact amount of transaction fee.")
        transaction_fee = self.__get_transfer_amount()

        if transaction_fee is None:
            return

        # Balance validation
        total_input = withdrawal_amount+transaction_fee
        if self.wallet.available_balance < total_input:
            print(self.ui.format_text("You do not have enough balance.", TEXT_COLOR.get("RED")))
            return

        # Create transaction
        transaction = Transaction(transaction_fee=transaction_fee)
        transaction.add_input(self.public_key, total_input)
        transaction.add_output(recipient[2], withdrawal_amount)

        # Get confirmation
        print(f"\nAre you sure you want to proceed with the following transaction:"
              f"\n{WHITESPACE}{transaction}")
        input(self.ui.PRESS_ENTER_TO_CONTINUE)

        transaction.sign(self.private_key)
        if transaction.is_valid():
            TransactionPool.add_transaction(transaction)
            self.transaction_client.broadcast_change(CRUD.get("ADD"), [transaction])
            print(self.ui.format_text("Your transfer is successfully initialised!", TEXT_COLOR.get("GREEN")))
        else:
            print(self.ui.format_text("Your transaction is invalid, please try again.", TEXT_COLOR.get("RED")))

    def log_out(self):
        self.is_logged_in = False
        self.database.log_out_node(self.username)
        self.node_client.broadcast_change(CRUD.get("UPDATE"), self)
        print("\nThanks for using GoodChain!")

    def cancel_pending_transaction(self):
        """ Cancels a pending transaction if possible """
        # Get applicable transactions
        pending_transactions = []
        for transaction in TransactionPool.get_transactions(with_reward_transactions=False):
            sender_public_key = transaction.input[0]
            receiver_public_key = transaction.output[0]
            if sender_public_key == self.public_key:
                pending_transactions.append(transaction)
            elif receiver_public_key == self.public_key:
                pending_transactions.append(transaction)

        if len(pending_transactions) < 1:
            error_text = "Only pending transactions can be cancelled, none where found."
            print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
            return

        # Show applicable transactions
        for i, transaction in enumerate(pending_transactions, start=1):
            print(f"[{i}] {transaction}")

        # Get transaction to cancel
        transaction_to_cancel = None
        print("Enter the ID of the transaction you'd like to cancel.")
        while transaction_to_cancel is None:
            transaction_id = input("ID " + self.ui.INPUT_ARROW).strip()
            try:
                transaction_id = int(transaction_id)
                if 0 < transaction_id <= len(pending_transactions):
                    transaction_index = transaction_id - 1
                    transaction_to_cancel = pending_transactions[transaction_index]
                    break
                else:
                    print(self.ui.INVALID_ID)
            except ValueError:
                print(self.ui.INVALID_ID)

        TransactionPool.remove_transactions([transaction_to_cancel])
        self.transaction_client.broadcast_change(CRUD.get("DELETE"), [transaction_to_cancel])
        print(self.ui.format_text("Your transaction is successfully canceled.", TEXT_COLOR.get("GREEN")))

    def __validate_mining_conditions(self, transaction_pool, is_genesis_block):
        """ Validates if GoodChain's mining conditions are met """
        # Transaction pool validation
        if 0 < len(transaction_pool) < MINIMUM_TRANSACTIONS:
            error_text = ("There are not enough transactions in the transaction pool, " +
                          f"there must be at least {MINIMUM_TRANSACTIONS} transactions.")
            print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
            return False

        # Time interval validation
        if not is_genesis_block:
            last_block = Ledger.get_last_block()
            last_block_creation_date = last_block.creation_date
            current_time = datetime.now()
            time_difference = current_time - last_block_creation_date
            required_time_difference_in_minutes = 3
            if time_difference < timedelta(minutes=required_time_difference_in_minutes):
                error_text = \
                    f"It has not been {required_time_difference_in_minutes} minutes since the last block's creation."
                print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
                return False
            # Last block validation
            verified_block_status = block_status.get("VERIFIED")
            if last_block.status != verified_block_status:
                error_text = f"You can not mine a new block until the latest is considered valid."
                print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
                return False

        # All checks passed
        return True

    def __get_transactions_to_mine(self, maximum_transactions, show_transactions=True):
        """ Returns the transactions the user is allowed to mine """
        chosen_transactions = []
        # Get the first 5 transactions by default
        all_transactions = TransactionPool.get_transactions()
        required_transactions = 5
        print(f"You are required to mine at least the following {required_transactions} transactions.")
        i = 0
        while i < required_transactions:
            transaction = all_transactions[i]
            print(WHITESPACE + f"{transaction}")
            chosen_transactions.append(transaction)
            i += 1

        # See if the user is still able to custom pick transactions
        transactions_to_chose = maximum_transactions-required_transactions
        print(f"You are allowed to choose {transactions_to_chose} transaction(s) your self.")
        # Let a user chose transactions if applicable
        if transactions_to_chose > 0:
            chosen_transaction_identities = []
            remaining_transactions = all_transactions[required_transactions:]

            # Show available transactions to choose from
            if show_transactions and transactions_to_chose > 0:
                for i, transaction in enumerate(remaining_transactions, start=1):
                    print(WHITESPACE + f"[{i}] {transaction}")

            # Handle user input
            print("Enter the identities of the transactions you'd like to mine one for one.")
            print(f"Note: the loop will stop soon as you reach {transactions_to_chose} distinct transactions "
                  f"or if you write 'done'.")
            while len(chosen_transactions) < maximum_transactions:
                transaction_id = input("ID " + self.ui.INPUT_ARROW).strip()
                try:
                    transaction_id = int(transaction_id) - 1
                    if transaction_id in chosen_transaction_identities:
                        error_text = "You have chosen this transaction already, please try another one."
                        print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
                    elif 0 <= transaction_id < len(remaining_transactions):
                        chosen_transaction_identities.append(transaction_id)
                        chosen_transactions.append(remaining_transactions[transaction_id])
                    else:
                        print(self.ui.INVALID_ID)
                except ValueError:
                    if transaction_id.lower() == "done":
                        if len(chosen_transactions) >= MINIMUM_TRANSACTIONS:
                            break
                        else:
                            error_text = (f"You must chose at least {MINIMUM_TRANSACTIONS-len(chosen_transactions)} " +
                                          "transaction(s) more.")
                            print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
                    else:
                        print(self.ui.INVALID_ID)
        return chosen_transactions

    def __flag_invalid_transactions(self, invalid_transactions: list[Transaction]):
        """ Returns the given transactions flagged as invalid """
        for invalid_transaction in invalid_transactions:
            invalid_transaction.valid = False
        return invalid_transactions

    def __get_recipient_node_by_username(self):
        """ Returns a node chosen by the user to send coins to """
        recipient_username = input("Write " + self.ui.BACK + " to go back.\n"
                                   "Username " + self.ui.INPUT_ARROW).strip()
        if recipient_username == 'back':
            return None
        recipient_node = self.database.get_node_by_username(recipient_username)
        if recipient_node and recipient_node[0] != self.username:
            return recipient_node
        else:
            error_text = f"No node with this username could be found, please try again."
            print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
            return self.__get_recipient_node_by_username()

    def __get_transfer_amount(self):
        """
        Prompts the user to specify the amount of coins to transfer.
        Returns the amount of coins the user would like to transfer.
        """
        amount = input("Write " + self.ui.BACK + " to go back.\n"
                       "Amount " + self.ui.INPUT_ARROW).strip()
        if amount == 'back':
            return None
        try:
            float_value = float(amount.replace(',', '.'))
            return float_value
        except ValueError:
            error_text = f"This is not an acceptable amount, please try again."
            print(self.ui.format_text(error_text, TEXT_COLOR.get("RED")))
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
