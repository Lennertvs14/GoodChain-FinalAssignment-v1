from block import block_status
from ledger import Ledger
from transaction import REWARD
from transaction_pool import TransactionPool
from user_interface import whitespace


class Wallet:
    """ Represents a digital tool that allows nodes to manage their currencies """
    def __init__(self, owner_node):
        self.owner = owner_node

    @property
    def transactions(self):
        """ Returns transaction history string """
        # Get transactions from ledger
        result = "PROCESSED TRANSACTIONS:\n"
        credit = []
        debet = []
        for block in Ledger.get_blocks():
            for transaction in block.data:
                receiver_public_key = transaction.output[0]
                if receiver_public_key == self.owner.public_key:
                    credit.append(transaction)
                elif transaction.type != REWARD and transaction.input[0] == self.owner.public_key:
                    debet.append(transaction)

        # Include grouped processed transactions
        if len(credit) > 0:
            result += "+ RECEIVED +\n"
            for t in credit:
                result += whitespace + f"{t}\n"
        if len(debet) > 0:
            result += "- SEND -\n"
            for t in debet:
                result += whitespace + f"{t}\n"

        result += "\n"

        # Get transactions from transaction pool
        result += "UNPROCESSED TRANSACTIONS:\n"
        credit = []
        debet = []
        for transaction in TransactionPool.get_transactions():
            receiver_public_key = transaction.output[0]
            if transaction.type == REWARD and receiver_public_key == self.owner.public_key:
                credit.append(transaction)
            elif transaction.type != REWARD and transaction.input[0] == self.owner.public_key:
                debet.append(transaction)

        # Include grouped unprocessed transactions
        if len(credit) > 0:
            result += "+ TO RECEIVE +\n"
            for t in credit:
                result += whitespace + f"{t}\n"
        if len(debet) > 0:
            result += "- TO SEND -\n"
            for t in debet:
                result += whitespace + f"{t}\n"

        return result

    @property
    def available_balance(self):
        """ Returns the available balance """
        incoming = 0.0
        outgoing = 0.0
        for block in Ledger.get_blocks():
            if block.status == block_status.get("VERIFIED"):
                for transaction in block.data: # processed transactions list
                    receiver_public_key = transaction.output[0]
                    if receiver_public_key == self.owner.public_key:
                        incoming += transaction.output[1]
                    elif transaction.type != REWARD and transaction.input[0] == self.owner.public_key:
                        outgoing += transaction.input[1]

        return incoming - outgoing
