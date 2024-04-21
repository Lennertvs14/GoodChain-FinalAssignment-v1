from block import Block
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from time import time


timing_variable = 20


class TransactionBlock(Block):
    def __init__(self, previous_block):
        super(TransactionBlock, self).__init__([], previous_block)

    def add_transaction(self, transaction):
        self.data.append(transaction)

    def is_valid(self):
        """ Returns whether each transaction in the data list is valid """
        if not super(TransactionBlock, self).is_valid():
            return False
        for t in self.data:
            if not t.is_valid():
                return False
        return True

    def mine(self, leading_zero):
        print("\nMining..")
        start_time = time()
        end_time = None

        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data), 'utf-8'))
        digest.update(bytes(str(self.previous_block_hash), 'utf-8'))

        # Search for nonce
        found = False
        nonce = 0
        while not found:
            new_digest = digest.copy()
            new_digest.update(bytes(str(nonce), 'utf-8'))
            new_hash = new_digest.finalize()
            if new_hash[:leading_zero] == bytes('0' * leading_zero, 'utf-8'):
                if int(new_hash[leading_zero]) < timing_variable and (time() - start_time) > 10:
                    found = True
                    end_time = time()
                    self.nonce = nonce
                elif (time() - start_time) > 20:
                    print("The mining process took too long, please try again later.")
                    return
            nonce += 1
            del new_digest

        computation_time = end_time - start_time
        self.block_hash = self.compute_hash()
        print(f"Block #{self.id} is mined in {computation_time} seconds.")
