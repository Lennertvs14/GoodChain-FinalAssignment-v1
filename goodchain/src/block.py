from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from datetime import datetime
from uuid import uuid4
from user_interface import whitespace


# Block statuses
block_status = {
    "UNVERIFIED": "UNVERIFIED",
    "VERIFIED": "VERIFIED"
}


class Block:
    data = None
    previous_block_hash = None
    creation_date = None
    miner = None
    validated_by = ""

    def __init__(self, data, previous_block):
        self.id = uuid4()
        self.data = data
        self.block_hash = None
        self.previous_block = previous_block
        self.nonce = 0
        if previous_block:
            self.previous_block_hash = previous_block.compute_hash()
        self.total_transaction_fee = 0
        self.valid_flags = 0
        self.invalid_flags = 0
        self.creation_date = datetime.now()
        self.status = block_status["UNVERIFIED"]

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

    def __repr__(self):
        result = ""

        result += f"Block ID: {str(self.id)}\n"
        result += whitespace + fr"Block hash value: {str(self.block_hash)}" + "\n"

        if self.previous_block:
            result += whitespace + fr"Previous block hash value: {str(self.previous_block_hash, encoding='utf-8')}" + "\n"

        result += whitespace + "Data:\n"
        for t in self.data:
            result += whitespace + whitespace
            result += f"{t}"
            result += "\n"

        result += whitespace + f"Mined by: {self.miner.username}\n"
        result += whitespace + f"Total transaction fee: {str(self.total_transaction_fee)}\n"
        result += whitespace + fr"Nonce: {str(self.nonce)}" + "\n"
        result += whitespace + f"Creation date: {str(self.creation_date)}\n"
        result += whitespace + f"Validated by: {str(self.validated_by)}\n"
        result += whitespace + f"Valid flags: {str(self.valid_flags)}\n"
        result += whitespace + f"Invalid flags: {str(self.invalid_flags)}\n"
        result += whitespace + f"Status: {str(self.status)}\n"

        return result
