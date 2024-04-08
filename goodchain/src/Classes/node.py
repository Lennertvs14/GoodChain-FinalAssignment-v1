from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


class Node:
    """ A Node represents a registered user. """

    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash
        self.private_key, self.public_key = self.__generate_serialized_keys()

    def __init__(self, username, password_hash, public_key, private_key):
        self.username = username
        self.password_hash = password_hash
        self.public_key = public_key
        self.private_key = private_key

    def __generate_serialized_keys(self):
        """ Returns a serialized cryptographic private- and public key object """
        # Generate keys
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        # Serialize keys
        serialized_private_key = private_key.private_bytes(
           encoding=serialization.Encoding.PEM,
           format=serialization.PrivateFormat.TraditionalOpenSSL,
           encryption_algorithm=serialization.NoEncryption()
        )
        serialized_public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return serialized_private_key, serialized_public_key
