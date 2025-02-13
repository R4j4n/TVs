import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def encrypt_password(password: str):
    """
    Encrypts a password and saves both the key and encrypted password
    Returns the encrypted password that you can put in auth.txt
    """
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(os.urandom(32)))

    # Save the key
    with open("auth/key.txt", "wb") as f:
        f.write(key + b"." + salt)

    # Encrypt the password
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())

    # Save to auth.txt
    with open("auth/auth.txt", "wb") as f:
        f.write(encrypted_password)

    print("Files created:")
    print("- key.txt: contains the encryption key")
    print("- auth.txt: contains your encrypted password")


# Use it like this:
if __name__ == "__main__":
    password = input("Enter the password you want to encrypt: ")
    encrypt_password(password)
