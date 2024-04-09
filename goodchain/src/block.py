from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


class Block:
    data = None
    previous_block_hash = None

    def __init__(self, data, previous_block=None):
        self.data = data
        self.block_hash = None
        self.previous_block = previous_block
        self.nonce = 0
        if previous_block:
            self.previous_block_hash = previous_block.compute_hash()

    def compute_hash(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data),'utf-8'))
        digest.update(bytes(str(self.previous_block_hash),'utf-8'))
        return digest.finalize()

    def is_valid(self):
        current_block_is_valid = self.block_hash == self.compute_hash()
        if self.previous_block:
            previous_block_is_valid = self.previous_block.is_valid()
            return current_block_is_valid and previous_block_is_valid
        else:
            return current_block_is_valid
