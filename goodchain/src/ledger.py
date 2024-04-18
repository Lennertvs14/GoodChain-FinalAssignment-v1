import pickle
from transaction_block import TransactionBlock
from user_interface import whitespace


path = "../data/ledger.dat"


class Ledger:
    """ Represents a 'immutable' record of all transactions that have been executed and shared among nodes """
    @staticmethod
    def add_block(block: TransactionBlock):
        """ Adds transaction block to the ledger """
        if block:
            with open(path, "ab") as ledger:
                pickle.dump(block, ledger)

    @staticmethod
    def show_ledger():
        """ Prints out the current ledger """
        blocks = Ledger.get_blocks()
        if blocks is not None and len(blocks) > 0:
            print("Blocks:")
            for block in blocks:
                print(whitespace + f"{block}")
        else:
            print("There are no blocks in our chain yet.")

    @staticmethod
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

    @staticmethod
    def get_last_block():
        """ Returns the last block out of the ledger or None """
        all_blocks = Ledger.get_blocks()
        if all_blocks is not None and len(all_blocks) > 0:
            return all_blocks[-1]
        else:
            return None
