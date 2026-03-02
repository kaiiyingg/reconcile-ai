"""
Simple authentication utilities: password matching
"""

def verify_password(plain_password: str, stored_password: str) -> bool:
    return plain_password == stored_password
