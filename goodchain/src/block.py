from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from datetime import datetime
from user_interface import UserInterface, WHITESPACE, TEXT_COLOR


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
        self.id = self.__get_unique_id()
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
        digest.update(bytes(str(self.data), 'utf-8'))
        digest.update(bytes(str(self.previous_block_hash), 'utf-8'))
        return digest.finalize()

    def is_valid(self):
        current_block_is_valid = self.block_hash == self.compute_hash()
        if self.previous_block:
            previous_block_is_valid = self.previous_block.is_valid()
            return current_block_is_valid and previous_block_is_valid
        else:
            return current_block_is_valid

    def __get_unique_id(self):
        from ledger import Ledger
        current_blocks = Ledger.get_blocks()
        if current_blocks is not None and len(current_blocks) > 0:
            return len(current_blocks)
        else:
            return 0

    def __repr__(self):
        result = ""

        result += f"Block ID: {str(self.id)}\n"
        result += WHITESPACE + fr"Block hash value: {str(self.block_hash)}" + "\n"

        if self.previous_block:
            result += WHITESPACE + fr"Previous block hash value: {str(self.previous_block_hash)}" + "\n"

        result += WHITESPACE + "Data:\n"
        for t in self.data:
            result += WHITESPACE + WHITESPACE
            result += f"{t}"
            result += "\n"

        result = UserInterface.format_text(result, TEXT_COLOR.get("CYAN"))

        result += WHITESPACE + f"Mined by: {self.miner.username}\n"
        result += WHITESPACE + f"Total transaction fee: {str(self.total_transaction_fee)}\n"
        result += WHITESPACE + fr"Nonce: {str(self.nonce)}" + "\n"
        result += WHITESPACE + f"Creation date: {str(self.creation_date)}\n"
        result += WHITESPACE + f"Validated by: {str(self.validated_by)}\n"
        result += WHITESPACE + f"Valid flags: {str(self.valid_flags)}\n"
        result += WHITESPACE + f"Invalid flags: {str(self.invalid_flags)}\n"
        result += WHITESPACE + f"Status: {str(self.status)}\n"

        return UserInterface.format_text(result, TEXT_COLOR.get("CYAN"))
