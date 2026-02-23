"""
JWT Authentication module
"""
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import hashlib

SECRET_KEY = "your-super-secret-jwt-key-change-in-production"
ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def create_token(user_id: str, username: str) -> Dict:
    """Create JWT token"""
    payload = {
        "user_id": user_id,
        "username": username,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": TOKEN_EXPIRY_HOURS * 3600
    }

def verify_token(token: str) -> Optional[Dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None
