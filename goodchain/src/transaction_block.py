from block import Block
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


timing_variable = 20


class TransactionBlock(Block):
    def __init__(self, previous_block):
        super(Block, self).__init__([], previous_block)

    def add_transaction(self, transaction):
        self.data.append(transaction)

    def is_valid(self):
        """ Returns whether each transaction in the data list is valid """
        if not super(Block, self).is_valid():
            return False
        for t in self.data:
            if not t.is_valid():
                return False
        return True

    def mine(self, leading_zero):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data), 'utf-8'))
        digest.update(bytes(str(self.previous_block_hash), 'utf-8'))

        found = False
        nonce = 0
        # Search for nonce
        while not found:
            new_digest = digest.copy()
            new_digest.update(bytes(str(nonce), 'utf-8'))
            new_hash = new_digest.finalize()
            if new_hash[:leading_zero] == bytes('0' * leading_zero, 'utf-8'):
                if int(new_hash[leading_zero]) < timing_variable:
                    found = True
                    self.nonce = nonce
            nonce += 1
            del new_digest

        self.block_hash = self.compute_hash()
