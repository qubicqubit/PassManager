import random
import string

def generate_password(length=12):
    """
    Generate a random secure password.

    Args:
        length (int): Desired password length (default 12).

    Returns:
        str: Randomly generated password.
    """
    if length < 6:
        raise ValueError("Password length should be at least 6 characters.")
    
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password 