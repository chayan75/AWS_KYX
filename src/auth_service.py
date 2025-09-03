#!/usr/bin/env python3
"""
Authentication service for KYC admin dashboard.
Handles user login, role management, and session management.
"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

class AuthService:
    """Service for handling user authentication and authorization."""
    
    def __init__(self):
        # JWT secret key - in production, use a secure secret
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
        self.jwt_algorithm = 'HS256'
        self.jwt_expiry_hours = 24
        
        # Predefined users - in production, store in database
        self.users = {
            'admin': {
                'username': 'admin',
                'password_hash': self._hash_password('admin'),
                'role': 'admin',
                'full_name': 'Administrator',
                'email': 'admin@company.com',
                'created_at': datetime.now().isoformat()
            },
            'user': {
                'username': 'user',
                'password_hash': self._hash_password('user'),
                'role': 'user',
                'full_name': 'Regular User',
                'email': 'user@company.com',
                'created_at': datetime.now().isoformat()
            }
        }
        
        # Active sessions (in production, use Redis or database)
        self.active_sessions = {}
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return self._hash_password(password) == password_hash
    
    def _generate_token(self, username: str, role: str) -> str:
        """Generate a JWT token for the user."""
        payload = {
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=self.jwt_expiry_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify a JWT token."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate a user and return login result."""
        if username not in self.users:
            return {
                'success': False,
                'message': 'Invalid username or password'
            }
        
        user = self.users[username]
        
        if not self._verify_password(password, user['password_hash']):
            return {
                'success': False,
                'message': 'Invalid username or password'
            }
        
        # Generate token
        token = self._generate_token(username, user['role'])
        
        # Store session
        session_id = secrets.token_urlsafe(32)
        self.active_sessions[session_id] = {
            'username': username,
            'role': user['role'],
            'token': token,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        return {
            'success': True,
            'message': 'Login successful',
            'token': token,
            'session_id': session_id,
            'user': {
                'username': username,
                'role': user['role'],
                'full_name': user['full_name'],
                'email': user['email']
            }
        }
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token and return user info."""
        payload = self._decode_token(token)
        if not payload:
            return None
        
        username = payload.get('username')
        if username not in self.users:
            return None
        
        user = self.users[username]
        return {
            'username': username,
            'role': user['role'],
            'full_name': user['full_name'],
            'email': user['email']
        }
    
    def verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Verify a session and return user info."""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        # Check if token is still valid
        user_info = self.verify_token(session['token'])
        if not user_info:
            # Remove expired session
            del self.active_sessions[session_id]
            return None
        
        # Update last activity
        session['last_activity'] = datetime.now().isoformat()
        
        return user_info
    
    def logout(self, session_id: str) -> bool:
        """Logout a user by removing their session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False
    
    def has_permission(self, user_role: str, action: str) -> bool:
        """Check if a user has permission to perform an action."""
        if user_role == 'admin':
            return True  # Admin can do everything
        
        if user_role == 'user':
            # User can only view, not modify
            read_only_actions = [
                'view_dashboard',
                'view_case_details',
                'view_documents',
                'view_audit_logs',
                'view_email_history'
            ]
            return action in read_only_actions
        
        return False
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information by username."""
        if username not in self.users:
            return None
        
        user = self.users[username]
        return {
            'username': user['username'],
            'role': user['role'],
            'full_name': user['full_name'],
            'email': user['email'],
            'created_at': user['created_at']
        }
    
    def list_users(self) -> list:
        """List all users (admin only)."""
        users = []
        for username, user in self.users.items():
            users.append({
                'username': user['username'],
                'role': user['role'],
                'full_name': user['full_name'],
                'email': user['email'],
                'created_at': user['created_at']
            })
        return users

# Global auth service instance
auth_service = AuthService() 