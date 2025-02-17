import base64
import json
import os
import secrets
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import APIKeyHeader


class PasswordManager:
    def __init__(self):
        self.auth_file = Path("server/auth/auth.txt")
        self.key_file = Path("server/auth/key.txt")
        self._initialize_key()

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

    def encrypt_password(self, password: str) -> bytes:
        """Encrypt a password"""
        return self.fernet.encrypt(password.encode())

    def decrypt_password(self, encrypted_password: bytes) -> str:
        """Decrypt a password"""
        return self.fernet.decrypt(encrypted_password).decode()

    def load_password(self) -> Optional[str]:
        """Load encrypted password from auth.txt"""
        if not self.auth_file.exists():
            return None

        try:
            with self.auth_file.open("rb") as f:
                encrypted_password = f.read().strip()
                print(encrypted_password)
            return self.decrypt_password(encrypted_password)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to load password: {str(e)}"
            )


# Session management
class SessionManager:
    def __init__(self):
        self.password_manager = PasswordManager()
        self.sessions = {}  # token -> expiry_time
        self.session_duration = timedelta(hours=24)  # Sessions last 24 hours

    def validate_password(self, password: str) -> bool:
        """Validate password against stored encrypted password"""
        stored_password = self.password_manager.load_password()
        if not stored_password:
            raise HTTPException(
                status_code=401, detail="No password has been set in auth.txt"
            )
        return password == stored_password

    def create_session(self, password: str) -> str:
        """Create a new session if password matches"""
        if not self.validate_password(password):
            raise HTTPException(status_code=401, detail="Invalid password")

            # Load existing key and salt
        with self.password_manager.key_file.open("rb") as f:
            data = f.read().split(b".")
            token = data[0]
        self.sessions[token] = datetime.now() + self.session_duration
        return token

    def validate_session(self, token: str) -> bool:
        """Check if session is valid and not expired"""
        if token not in self.sessions:
            return False

        if datetime.now() > self.sessions[token]:
            # Clean up expired session
            del self.sessions[token]
            return False

        return True

    def end_session(self, token: str) -> None:
        """End a specific session"""
        if token in self.sessions:
            del self.sessions[token]


# Create global session manager
session_manager = SessionManager()
