from database import path as database_path
from hashlib import sha256
from ledger import path as ledger_path
from transaction import Transaction, REWARD
from transaction_pool import TransactionPool, path as transaction_pool_path


system_hash_path = "../data/system.dat"


class System:
    """ Represents the system-level operations and checks in the application """
    @staticmethod
    def grant_reward(receiver_node, amount: float):
        """ Grants a reward to a node by initializing a transaction """
        reward_transaction = Transaction(transaction_type=REWARD)
        reward_transaction.add_output(receiver_node.public_key, amount)
        reward_transaction.valid = True # System created transactions such as reward transactions are always valid
        TransactionPool.add_transaction(reward_transaction)

    def __init__(self):
        self.system_hash = self.__get_system_hash()

    def is_data_integrity_preserved(self):
        """ Returns whether the system's data files are not tampered with """
        current_system_hash = self.__compute_hash()
        if not self.system_hash == current_system_hash:
            print("System startup aborted: Integrity check failed.\n"
                  "Unauthorized modifications have been detected in the system files.\n"
                  "Undo your modifications or contact GoodChain's helpdesk for support (support@goodchain.com).")
            self.exit()
        else:
            return True

    def exit(self):
        """ Exits the system in the right way """
        current_system_hash = self.__compute_hash()
        self.__set_system_hash(current_system_hash)
        exit()

    def __get_system_hash(self):
        saved_system_hash = ""
        try:
            with open(system_hash_path, "r") as file:
                while True:
                    data = file.read()
                    if not data:
                        break
                    saved_system_hash += data
        except FileNotFoundError:
            # There is no such data file
            pass
        except EOFError:
            # No more lines to read from file
            pass
        if not saved_system_hash:
            saved_system_hash = self.__compute_hash()
            self.__set_system_hash(saved_system_hash)
        return saved_system_hash

    def __set_system_hash(self, system_hash):
        """ Sets system hash to the data file """
        with open(system_hash_path, "wb") as file:
            file.write(bytes(system_hash, 'utf-8'))

    def __compute_hash(self):
        digest = sha256()

        database = self.__get_file_data(database_path)
        if database is not None:
            digest.update(database)

        ledger = self.__get_file_data(ledger_path)
        if ledger is not None:
            digest.update(ledger)

        transaction_pool = self.__get_file_data(transaction_pool_path)
        if transaction_pool is not None:
            digest.update(transaction_pool)

        return digest.hexdigest()

    def __get_file_data(self, path):
        data = b''
        try:
            with open(path, "rb") as file:
                while True:
                    chunk = file.read(65536)
                    if not chunk:
                        break
                    data += chunk  # Concatenate the chunks
        except FileNotFoundError:
            # There is no such data file
            pass
        except EOFError:
            # No more lines to read from file
            pass
        return data
