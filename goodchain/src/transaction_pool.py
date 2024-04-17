import pickle
from transaction import Transaction


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
    def flag_invalid_transactions(invalid_transactions: list[Transaction]):
        """ Sets the given transactions as invalid and updates the pool """
        transactions = TransactionPool.get_transactions()
        for transaction in transactions:
            for invalid_transaction in invalid_transactions:
                if transaction.id == invalid_transaction.id:
                    transaction.valid = False
                    break

        # Overwrite transaction pool file
        with open(path, "wb") as pool:
            for transaction in transactions:
                pickle.dump(transaction, pool)

    @staticmethod
    def show_transaction_pool():
        """ Prints the current transaction pool """
        print("Transaction pool:")
        transactions = TransactionPool.get_transactions()
        whitespace = "    "
        transaction_count = 1
        if transactions and len(transactions) > 0:
            for transaction in transactions:
                if transaction:
                    print(f"{whitespace} [{transaction_count}] {transaction}")
                    transaction_count += 1
        else:
            print(whitespace + "No transactions found.")

    @staticmethod
    def get_transactions():
        """ Returns a list of transactions out of the pool """
        transactions = []
        try:
            with open(path, "rb") as pool:
                while True:
                    transaction = pickle.load(pool)
                    transactions.append(transaction)
        except FileNotFoundError:
            # There is no transaction pool yet.
            pass
        except EOFError:
            # No more lines to read from file.
            pass
        return transactions
