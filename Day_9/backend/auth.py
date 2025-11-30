"""
User Authentication System for Day 9 E-commerce Agent
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# File paths
USERS_PATH = Path(__file__).parent / "users.json"

# In-memory users storage
USERS = {}

# Load existing users if file exists
if USERS_PATH.exists():
    with open(USERS_PATH) as f:
        USERS = json.load(f)


def save_users():
    """Save users to JSON file"""
    with open(USERS_PATH, 'w') as f:
        json.dump(USERS, f, indent=2)


def hash_password(password: str) -> str:
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(email: str, password: str, name: str, phone: str, address: str) -> Optional[Dict[str, Any]]:
    """Create a new user account"""
    if email in USERS:
        return None  # User already exists
    
    user = {
        "email": email,
        "password": hash_password(password),
        "name": name,
        "phone": phone,
        "address": address,
        "created_at": datetime.now().isoformat()
    }
    
    USERS[email] = user
    save_users()
    
    # Return user without password
    user_safe = user.copy()
    del user_safe["password"]
    return user_safe


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user login"""
    if email not in USERS:
        return None
    
    user = USERS[email]
    if user["password"] != hash_password(password):
        return None
    
    # Return user without password
    user_safe = user.copy()
    del user_safe["password"]
    return user_safe


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email (without password)"""
    if email not in USERS:
        return None
    
    user = USERS[email].copy()
    del user["password"]
    return user