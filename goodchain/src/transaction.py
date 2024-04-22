from database import Database
import signature
from uuid import uuid4


NORMAL = 0
REWARD = 1


class Transaction:
    input = None
    output = None
    signature = None
    extra_required_signature = None

    def __init__(self, transaction_type=NORMAL, transaction_fee=0):
        self.id = uuid4()
        self.type = transaction_type
        self.transaction_fee = transaction_fee
        self.valid = None # To be determined by mining process

    def add_input(self, from_addr, amount):
        self.input = (from_addr, amount)

    def add_output(self, to_addr, amount):
        self.output = (to_addr, amount)

    def add_extra_required_signature(self, addr):
        self.extra_required_signature = addr

    def sign(self, private):
        message = self.__gather_transaction_data()
        new_signature = signature.sign(message, private)
        self.signature = new_signature

    def is_valid(self):
        """ Returns whether a transaction is valid or not """
        if self.type == REWARD:
            if self.input and self.output:
                return False
            else:
                return True
        else:
            total_in = 0
            total_out = 0
            message = self.__gather_transaction_data()

            # Validate input
            addr, amount = self.input
            # Do not allow a negative input amount
            if amount < 0 or amount == 0:
                return False
            # Validate signature
            if not signature.verify(message, self.signature, addr):
                return False
            total_in = total_in + amount

            # Validate extra required signatures
            if self.extra_required_signature:
                if not signature.verify(message, self.signature, self.extra_required_signature):
                    return False

            # Validate output
            addr, amount = self.output
            if amount < 0 or amount == 0:
                return False
            total_out = total_out + amount

            # Outputs must not exceed inputs
            if total_out > total_in:
                return False

            return True

    def __gather_transaction_data(self):
        """ Returns a list of transaction data """
        return [self.input, self.output, self.extra_required_signature]

    def __repr__(self):
        db = Database()
        result = "From: "
        if self.input and self.type == NORMAL:
            sender_username = db.get_node_username_by_public_key(self.input[0])
            result += sender_username
        else:
            result += "REWARD SYSTEM"

        result += " | To: "
        receiver_username = db.get_node_username_by_public_key(self.output[0])
        result += receiver_username

        result += " | Amount: "
        result += str(self.output[1])

        result += " | Transaction fee: "
        result += str(self.transaction_fee)

        if self.type != REWARD and self.valid:
            result += " | Is valid: "
            result += str(self.valid)
        return result
