# crypto_utils.py
# -------------------------------------------------------
# This module handles encryption and decryption operations
# for the Secure Password Manager application.
#
# WHY THIS FILE EXISTS:
# Passwords stored by users must never be kept in plaintext.
# This module ensures that passwords and sensitive data
# are securely encrypted using AES-256 before being saved to the vault database.
#
# DESIGN DECISIONS:
# - AES encryption in CBC mode is used for strong symmetric encryption.
# - PBKDF2 key derivation is used to transform the user's master password into a secure AES key.
# - Random salt and IV are generated for each encryption to maximize security.
# - Base64 encoding is used to make encrypted blobs safe for storage.
#
# HOW THIS MODULE FITS THE FULL APPLICATION:
# - Master password entered during login (handled in auth.py) will also be used here for vault encryption.
# - When a user saves a password, encrypt_data() secures it.
# - When a user views a password, decrypt_data() unlocks it securely.
#
# This ensures the application provides true confidentiality: 
# even if the database is stolen, passwords remain unreadable without the master password.
# -------------------------------------------------------

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

# --- Constants ---

SALT_SIZE = 16  # Size of salt in bytes (128 bits)
IV_SIZE = 16    # Size of AES IV (AES block size is 128 bits)
KEY_SIZE = 32   # Key size in bytes for AES-256 (256 bits)
ITERATIONS = 100_000  # PBKDF2 iterations to slow down brute-force attacks

# --- Key Derivation ---

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a secure AES encryption key from a master password and a salt.

    Args:
        password (str): The user's master password.
        salt (bytes): A random salt to ensure uniqueness.

    Returns:
        bytes: A strong symmetric key for AES encryption.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

# --- Encryption ---

def encrypt_data(plaintext: str, password: str) -> str:
    """
    Encrypt plaintext data using a password-derived AES key.

    The output is a base64-encoded blob containing salt + IV + ciphertext.

    Args:
        plaintext (str): The data to encrypt (e.g., a user's saved password).
        password (str): The user's master password.

    Returns:
        str: Base64-encoded encrypted data.
    """
    salt = os.urandom(SALT_SIZE)  # Random salt for uniqueness
    key = derive_key(password, salt)  # Derive strong encryption key
    iv = os.urandom(IV_SIZE)  # Random IV for AES CBC mode

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad plaintext to a multiple of AES block size (16 bytes)
    padded_plaintext = plaintext.encode()
    while len(padded_plaintext) % 16 != 0:
        padded_plaintext += b' '  # Simple space padding

    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    # Combine salt + IV + ciphertext together
    encrypted_blob = salt + iv + ciphertext

    # Encode combined blob as base64 for storage
    return base64.b64encode(encrypted_blob).decode()

# --- Decryption ---

def decrypt_data(encrypted_data: str, password: str) -> str:
    """
    Decrypt data previously encrypted with encrypt_data().

    Args:
        encrypted_data (str): Base64-encoded encrypted blob.
        password (str): The user's master password.

    Returns:
        str: The original decrypted plaintext.
    """
    encrypted_blob = base64.b64decode(encrypted_data)  # Decode from base64

    # Extract salt, IV, and ciphertext
    salt = encrypted_blob[:SALT_SIZE]
    iv = encrypted_blob[SALT_SIZE:SALT_SIZE + IV_SIZE]
    ciphertext = encrypted_blob[SALT_SIZE + IV_SIZE:]

    # Derive encryption key again using extracted salt
    key = derive_key(password, salt)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Remove padding (trailing spaces)
    plaintext = padded_plaintext.rstrip(b' ')

    return plaintext.decode()
