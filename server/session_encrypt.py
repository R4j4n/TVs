import base64
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from fastapi import HTTPException


class AuthManager:
    def __init__(self):
        self.auth_file = Path("server/auth/auth.txt")
        self.key_file = Path("server/auth/key.txt")
        self._initialize_key()
        self.stored_password = None
        self._load_password()

    def _initialize_key(self):
        """Initialize or load encryption key"""
        if not self.key_file.exists():
            # Generate a new key
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(os.urandom(32)))
            # Save key and salt
            with self.key_file.open("wb") as f:
                f.write(key + b"." + salt)
        else:
            # Load existing key and salt
            with self.key_file.open("rb") as f:
                data = f.read().split(b".")
                key = data[0]

        self.fernet = Fernet(key)

    def _load_password(self):
        """Load encrypted password from auth.txt"""
        if not self.auth_file.exists():
            raise HTTPException(
                status_code=500,
                detail="No password set. Please create auth.txt with an encrypted password",
            )

        try:
            with self.auth_file.open("rb") as f:
                encrypted_password = f.read().strip()
                self.stored_password = self.fernet.decrypt(encrypted_password).decode()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to load password: {str(e)}"
            )

    def encrypt_password(self, password: str) -> bytes:
        """Encrypt a password"""
        return self.fernet.encrypt(password.encode())

    def validate_password(self, password: str) -> bool:
        """Validate password against stored encrypted password"""
        if not self.stored_password:
            raise HTTPException(
                status_code=500, detail="No password has been set in auth.txt"
            )
        return password == self.stored_password

    def get_api_key(self, password: str) -> str:
        """Get API key if password matches"""
        if not self.validate_password(password):
            raise HTTPException(status_code=401, detail="Invalid password")
        return self.stored_password  # Return the decrypted password as API key

    def verify_api_key(self, api_key: str) -> bool:
        """Verify if the provided API key is valid"""
        return api_key == self.stored_password


# Utility function to set up initial password
def setup_password(password: str, auth_file_path: str = "server/auth/auth.txt"):
    """
    Utility function to set up the initial encrypted password.
    This should be run once to set up the authentication system.
    """
    auth_manager = AuthManager()
    encrypted_password = auth_manager.encrypt_password(password)

    # Ensure directory exists
    Path(auth_file_path).parent.mkdir(parents=True, exist_ok=True)

    # Save encrypted password
    with open(auth_file_path, "wb") as f:
        f.write(encrypted_password)

    print("Password has been encrypted and saved successfully!")


# Create global auth manager
auth_manager = AuthManager()
