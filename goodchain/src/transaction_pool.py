import pickle
from transaction import Transaction, REWARD
from user_interface import whitespace


path = "../data/transaction_pool.dat"


class TransactionPool:
    """ Represents a collection of transactions waiting to be validated and included in a block by miners """

    @staticmethod
    def add_transaction(transaction: Transaction):
        """ Adds transaction to the pool """
        if transaction:
            with open(path, "ab") as pool:
                pickle.dump(transaction, pool)

    @staticmethod
    def remove_transactions(transactions: list[Transaction]):
        """ Removes transactions from the pool """
        current_transactions = TransactionPool.get_transactions()
        transactions_to_keep = [tx for tx in current_transactions if not any(t.id == tx.id for t in transactions)]

        # Overwrite transaction pool file
        with open(path, "wb") as pool:
            for transaction in transactions_to_keep:
                pickle.dump(transaction, pool)

    @staticmethod
    def update_transactions(updated_transactions: list[Transaction]):
        """ Updates the pool with the passed transactions """
        transactions = TransactionPool.get_transactions()

        # Create a dictionary of updated transactions for quick lookup
        updated_transactions_dict = {ut.id: ut for ut in updated_transactions}

        # Update transactions in the pool
        for i, transaction in enumerate(transactions):
            if transaction.id in updated_transactions_dict:
                transactions[i] = updated_transactions_dict[transaction.id]

        # Write the updated transactions back to the file
        with open(path, "wb") as pool:
            for transaction in transactions:
                pickle.dump(transaction, pool)

    @staticmethod
    def show_transaction_pool(with_reward_transactions=True, with_invalid_transactions=True):
        """ Prints the current transaction pool """
        print("Transaction pool:")
        transactions = TransactionPool.get_transactions()
        if transactions and len(transactions) > 0:
            for i, transaction in enumerate(transactions, start=1):
                if transaction and (with_reward_transactions or transaction.type != REWARD):
                    if not with_invalid_transactions and transaction.valid == False:
                        continue
                    print(whitespace + f"[{i}] {transaction}")
        else:
            print(whitespace + "No transactions found.")

    @staticmethod
    def get_transactions(with_reward_transactions=True):
        """ Returns a list of transactions out of the pool """
        transactions = []
        try:
            with open(path, "rb") as pool:
                while True:
                    transaction = pickle.load(pool)
                    if with_reward_transactions or transaction.type != REWARD:
                        transactions.append(transaction)
        except FileNotFoundError:
            # There is no transaction pool yet.
            pass
        except EOFError:
            # No more lines to read from file.
            pass
        return transactions
