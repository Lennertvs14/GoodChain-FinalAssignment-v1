import pickle
from transaction_block import TransactionBlock


path = "../data/ledger.dat"


def add_block(block: TransactionBlock):
    """ Adds transaction block to the ledger """
    if block:
        with open(path, "ab") as ledger:
            pickle.dump(block, ledger)


def show_ledger():
    """ Prints out the current ledger """
    blocks = get_blocks()
    for block in blocks:
        if block:
            print(block)


def get_blocks():
    """ Returns a list of blocks out of the ledger """
    blocks = []
    try:
        with open(path, "rb") as ledger:
            while True:
                block = pickle.load(ledger)
                blocks.append(block)
    except FileNotFoundError:
        # There is no ledger yet
        pass
    except EOFError:
        # No more lines to read from file
        pass
    return blocks

def get_last_block():
    """ Returns the last block out of the ledger or None """
    all_blocks = get_blocks()
    if all_blocks is not None and len(all_blocks) > 0:
        return all_blocks[-1]
    else:
        return None
