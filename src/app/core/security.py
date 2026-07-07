"""
Security module for handling password hashing and verification.

This module utilizes `pwdlib` to provide strong, up-to-date cryptographic
hashing for user passwords, ensuring secure storage in the database.
"""

from pwdlib import PasswordHash

# Initialize the password hasher with recommended settings (e.g., Argon2 or Bcrypt)
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using the recommended cryptographic algorithm.

    Args:
        password (str): The plain-text password provided by the user.

    Returns:
        str: The securely hashed password string.
    """
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a previously hashed password.

    Args:
        plain_password (str): The plain-text password attempting to authenticate.
        hashed_password (str): The hashed password retrieved from the database.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return password_hasher.verify(plain_password, hashed_password)
