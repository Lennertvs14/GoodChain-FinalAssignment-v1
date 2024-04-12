import pickle
from transaction import Transaction


path = "../data/transaction_pool.dat"


def add_transaction(transaction: Transaction):
    """ Adds transaction to the pool """
    if transaction and transaction.is_valid():
        with open(path, "ab") as pool:
            pickle.dump(transaction, pool)
    else:
        ValueError("Invalid transaction")


def check_pool():
    """ Prints out the current transaction pool """
    transactions = []
    try:
        with open(path, "rb") as f:
            while True:
                transaction = pickle.load(f)
                transactions.append(transaction)
    except EOFError:
        # No more lines to read from file.
        pass

    transaction_count = 1
    while transaction_count <= len(transactions):
        print(f"[{transaction_count}] {transaction}")
        transaction_count += 1
