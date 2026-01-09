"""
Authentication and authorization module
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.core.config import settings

# Security scheme
security = HTTPBearer()

class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None
    user_id: Optional[str] = None
    permissions: list = []

class User(BaseModel):
    """User model"""
    id: str
    username: str
    email: str
    permissions: list = []
    is_active: bool = True

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        permissions: list = payload.get("permissions", [])
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(username=username, user_id=user_id, permissions=permissions)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from token"""
    token = credentials.credentials
    token_data = verify_token(token)
    
    # For MVP, we'll use a simple user ID
    # In production, you'd want to fetch user details from a database
    return token_data.user_id or token_data.username

async def get_current_user_with_permissions(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user with permissions"""
    token = credentials.credentials
    token_data = verify_token(token)
    
    # Mock user for MVP - in production, fetch from database
    user = User(
        id=token_data.user_id or "default_user",
        username=token_data.username or "default_user",
        email=f"{token_data.username}@example.com",
        permissions=token_data.permissions
    )
    
    return user

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_checker(user: User = Depends(get_current_user_with_permissions)):
        if permission not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return user
    return permission_checker

# Mock user management for MVP
class MockUserManager:
    """Mock user manager for development"""
    
    def __init__(self):
        self.users = {
            "admin": User(
                id="admin",
                username="admin",
                email="admin@example.com",
                permissions=["read", "write", "admin", "approve"]
            ),
            "user": User(
                id="user",
                username="user",
                email="user@example.com",
                permissions=["read", "write"]
            ),
            "viewer": User(
                id="viewer",
                username="viewer",
                email="viewer@example.com",
                permissions=["read"]
            )
        }
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users.get(username)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user (mock implementation)"""
        # In production, verify password hash
        if username in self.users and password == "password":
            return self.users[username]
        return None
    
    def create_user(self, username: str, email: str, permissions: list = None) -> User:
        """Create a new user"""
        user_id = f"user_{len(self.users) + 1}"
        user = User(
            id=user_id,
            username=username,
            email=email,
            permissions=permissions or ["read"]
        )
        self.users[username] = user
        return user

# Global user manager instance
user_manager = MockUserManager()

# Authentication endpoints (for completeness)
async def login(username: str, password: str) -> Optional[str]:
    """Login user and return access token"""
    user = user_manager.authenticate_user(username, password)
    if not user:
        return None
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "permissions": user.permissions
        },
        expires_delta=access_token_expires
    )
    
    return access_token 