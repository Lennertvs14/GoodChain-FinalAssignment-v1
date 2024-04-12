from database import get_node_username_by_public_key
import signature
import uuid


NORMAL = 0
REWARD = 1


class Transaction:
    input = None
    output = None
    signature = None
    extra_required_signature = None

    def __init__(self, transaction_type=NORMAL, transaction_fee=0):
        self.id = uuid.uuid4()
        self.type = transaction_type
        self.transaction_fee = transaction_fee

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

            # Search for valid signatures
            for addr, amount in self.input:
                found = False
                # Do not allow a negative input amount
                if amount < 0:
                    return False
                for s in self.signature:
                    if signature.verify(message, s, addr):
                        found = True
                if not found:
                    return False
                total_in = total_in + amount

            # Search for valid extra required signatures
            for addr in self.extra_required_signature:
                found = False
                for s in self.signature:
                    if signature.verify(message, s, addr):
                        found = True
                if not found:
                    return False
            for addr, amount in self.output:
                if amount < 0:
                    return False
                total_out = total_out + amount

            # Outputs must not exceed inputs
            if total_out > total_in:
                return False

            return True

    def __gather_transaction_data(self):
        """ Returns a list of transaction data """
        return [self.input, self.output, self.extra_required_signature]

