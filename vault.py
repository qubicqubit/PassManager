import sqlite3
import os
from crypto_utils import encrypt_data
from crypto_utils import decrypt_data

# Create ~/.config/PassManager/ if it doesn't exist
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "PassManager")
os.makedirs(CONFIG_DIR, exist_ok=True)

VAULT_DB = os.path.join(CONFIG_DIR, "vault.db")

def initialize_database():
    # Connect to the SQLite database (creates the file if not exists)
    conn = sqlite3.connect(VAULT_DB)
    cursor = conn.cursor()

    # Creates the passwords table
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   website TEXT NOT NULL,
                   username TEXT NOT NULL,
                   password TEXT NOT NULL,
                   notes TEXT
               )
        ''')
    
    # Save (commit) the changes and close the connection
    conn.commit()
    conn.close()

def entry_exists(website: str, username: str) -> bool:
    conn = sqlite3.connect(VAULT_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM passwords WHERE website = ? AND username = ?", (website,username))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def add_password(website: str, username: str, plain_password: str, notes: str, master_password: str):
    conn = sqlite3.connect(VAULT_DB)
    cursor = conn.cursor()

    # Encrypt the password and notes before saving
    encrypted_password = encrypt_data(plain_password, master_password)
    encrypted_notes = encrypt_data(notes, master_password)

    # Insert the new record into the database
    cursor.execute('''
        INSERT INTO passwords (website, username, password, notes)
        VALUES (?, ?, ?, ?)
    ''', (website, username, encrypted_password, encrypted_notes))

    conn.commit()
    conn.close()


def get_all_passwords(master_password: str) -> list:
    conn = sqlite3.connect(VAULT_DB)
    cursor = conn.cursor()

    cursor.execute('SELECT id, website, username, password, notes FROM passwords')
    rows = cursor.fetchall()

    conn.close()

    decrypted_entries = []

    for row in rows:
        id_, website, username, encrypted_password, encrypted_notes = row

        # Decrypt sensitive fields
        decrypted_password = decrypt_data(encrypted_password, master_password)
        decrypted_notes = decrypt_data(encrypted_notes, master_password)

        # Build a clean entry
        entry = {
            "id": id_,
            "website": website,
            "username": username,
            "password":decrypted_password,
            "notes": decrypted_notes
        }

        decrypted_entries.append(entry)

    return decrypted_entries

def delete_password(entry_id: int):
    conn = sqlite3.connect(VAULT_DB)
    cursor = conn.cursor()

    # Delete the record by ID
    cursor.execute('DELETE FROM passwords WHERE id = ?', (entry_id,))

    conn.commit()
    conn.close()

def update_password(entry_id: int, new_website: str, new_username: str, new_plain_password: str, new_notes: str, master_password: str):
    conn = sqlite3.connect(VAULT_DB)
    cursor = conn.cursor()

    # Encrypt the new password and notes
    encrypted_password = encrypt_data(new_plain_password, master_password)
    encrypted_notes = encrypt_data(new_notes, master_password)

    # Update the record with new values
    cursor.execute('''
        UPDATE passwords
        SET website = ?, username = ?, password = ?, notes = ?
        WHERE id = ? 
    ''', (new_website, new_username, encrypted_password, encrypted_notes, entry_id))

    conn.commit()
    conn.close()
