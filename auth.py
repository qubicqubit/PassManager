import hashlib
import os
from platformdirs import user_config_dir

# --- Authentication and Master Password Management ---

# This file handles the creation, storage, and verification
# of the master password that secures the password manager vault.

# The master password is never stored directly.
# Instead, it is hashed using SHA-256 and saved securely in a local file.

# Path where the hashed master password will be stored.
# This file is created during first-time setup.

APP_NAME = "PassManager"
CONFIG_DIR = user_config_dir(APP_NAME)
#CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "PassManager")
os.makedirs(CONFIG_DIR, exist_ok=True)

MASTER_FILE = os.path.join(CONFIG_DIR, "master.key")

# Hashes a plaintext password using the SHA-256 algorithm.
# Converts the password into bytes (UTF-8 encoding) before hashing,
# and returns the digest as a human-readable hex string for easy storage and comparison.
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Checks whether the master password has already been set.
# This is determined by checking for the existence of the master key file.
# - If the file exists, the user can proceed to login.
# - If not, the user must complete first-time setup.
def is_master_set() -> bool:
    if not os.path.exists(MASTER_FILE):
        return False
    try:
        with open(MASTER_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return bool(content) and len(content) == 64
    except Exception:
        return False

# Saves a new master password securely.
# Hashes the provided password and writes the resulting hash into the master key file.
# This function is used only once during first-time setup.
def set_master_password(password: str):
    hashed = hash_password(password)
    with open(MASTER_FILE, 'w') as f:
        f.write(hashed)

# Verifies the user's input during login.
# Hashes the entered password and compares it against the stored master password hash.
# Returns True if the input is correct, otherwise returns False.
def verify_master_password(input_password: str) -> bool:
    if not is_master_set():
        return False
    try:
        with open(MASTER_FILE, 'r', encoding='utf-8') as f:
            stored_hash = f.read().strip()
        return hash_password(input_password) == stored_hash
    except Exception:
        return False
