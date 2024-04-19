from ledger import Ledger
from transaction_pool import TransactionPool


class Wallet:
    """ Represents a digital tool that allows nodes to manage their currencies """
    def __init__(self, owner_node):
        self.owner = owner_node

    @property
    def transactions(self):
        """ Returns processed transactions """
        # Get transactions from ledger
        processed_transactions = []
        blocks = Ledger.get_blocks()
        for block in blocks:
            # Get processed transactions
            # public key asserts
            pass
        return processed_transactions

    @property
    def available_balance(self):
        """ Returns the available balance """
        incoming = 0.0
        outgoing = 0.0
        for block in Ledger.get_blocks():
            for transaction in block.data: # processed transactions list
                sender_public_key = transaction.input[0]
                receiver_public_key = transaction.output[0]
                if sender_public_key == self.owner.public_key:
                    outgoing += transaction.input[1]
                elif receiver_public_key == self.owner.public_key:
                    incoming += transaction.output[1]

        result = incoming - outgoing

        pending_transactions = TransactionPool.get_transactions()
        for transaction in pending_transactions:
            if transaction.valid:
                # Reward transactions
                receiver_public_key = transaction.output[0]
                if receiver_public_key == self.owner.public_key:
                    incoming = transaction.output[1]
                    result += incoming

        return result
