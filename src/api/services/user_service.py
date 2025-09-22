"""
User service for the Engineering Log Intelligence System.
Handles user CRUD operations and business logic.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import structlog

from ..models.user import User
from ..utils.database import get_database_manager

logger = structlog.get_logger(__name__)


class UserService:
    """Service for managing user data and operations."""
    
    def __init__(self):
        """Initialize the user service."""
        self.db = get_database_manager()
        logger.info("User service initialized")
    
    def create_user(self, user: User) -> User:
        """Create a new user."""
        try:
            # Validate user data
            errors = user.validate()
            if errors:
                raise ValueError(f"User validation failed: {', '.join(errors)}")
            
            # Check if username or email already exists
            if self.get_user_by_username(user.username):
                raise ValueError("Username already exists")
            
            if self.get_user_by_email(user.email):
                raise ValueError("Email already exists")
            
            # Set timestamps
            now = datetime.now(timezone.utc)
            user.created_at = now
            user.updated_at = now
            
            # Insert user into database
            query, params = user.get_database_insert_query()
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, params)
                user_id = cursor.fetchone()[0]
                user.id = user_id
                cursor.connection.commit()
            
            logger.info("User created successfully", user_id=user.id, username=user.username)
            return user
            
        except Exception as e:
            logger.error("Failed to create user", error=str(e), username=user.username)
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        try:
            query = "SELECT * FROM users WHERE id = %s"
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()
                
                if row:
                    user = User.from_database_row(dict(row))
                    logger.info("User retrieved by ID", user_id=user_id, username=user.username)
                    return user
                else:
                    logger.info("User not found by ID", user_id=user_id)
                    return None
                    
        except Exception as e:
            logger.error("Failed to get user by ID", error=str(e), user_id=user_id)
            raise
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        try:
            query = "SELECT * FROM users WHERE username = %s"
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (username,))
                row = cursor.fetchone()
                
                if row:
                    user = User.from_database_row(dict(row))
                    logger.info("User retrieved by username", username=username, user_id=user.id)
                    return user
                else:
                    logger.info("User not found by username", username=username)
                    return None
                    
        except Exception as e:
            logger.error("Failed to get user by username", error=str(e), username=username)
            raise
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        try:
            query = "SELECT * FROM users WHERE email = %s"
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (email,))
                row = cursor.fetchone()
                
                if row:
                    user = User.from_database_row(dict(row))
                    logger.info("User retrieved by email", email=email, user_id=user.id)
                    return user
                else:
                    logger.info("User not found by email", email=email)
                    return None
                    
        except Exception as e:
            logger.error("Failed to get user by email", error=str(e), email=email)
            raise
    
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """Get a user by API key."""
        try:
            query = "SELECT * FROM users WHERE api_key = %s AND is_active = true"
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (api_key,))
                row = cursor.fetchone()
                
                if row:
                    user = User.from_database_row(dict(row))
                    logger.info("User retrieved by API key", user_id=user.id, username=user.username)
                    return user
                else:
                    logger.info("User not found by API key", api_key=api_key[:10] + "...")
                    return None
                    
        except Exception as e:
            logger.error("Failed to get user by API key", error=str(e))
            raise
    
    def get_all_users(self, limit: int = 100, offset: int = 0, active_only: bool = True) -> List[User]:
        """Get all users with pagination."""
        try:
            query = "SELECT * FROM users"
            params = []
            
            if active_only:
                query += " WHERE is_active = true"
            
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                users = [User.from_database_row(dict(row)) for row in rows]
                logger.info("Users retrieved", count=len(users), limit=limit, offset=offset)
                return users
                
        except Exception as e:
            logger.error("Failed to get all users", error=str(e))
            raise
    
    def search_users(self, query: str, limit: int = 50) -> List[User]:
        """Search users by username, email, or name."""
        try:
            search_query = """
                SELECT * FROM users 
                WHERE (username ILIKE %s OR email ILIKE %s OR 
                       first_name ILIKE %s OR last_name ILIKE %s)
                AND is_active = true
                ORDER BY username
                LIMIT %s
            """
            
            search_term = f"%{query}%"
            params = [search_term, search_term, search_term, search_term, limit]
            
            with self.db.get_cursor() as cursor:
                cursor.execute(search_query, params)
                rows = cursor.fetchall()
                
                users = [User.from_database_row(dict(row)) for row in rows]
                logger.info("Users searched", query=query, count=len(users))
                return users
                
        except Exception as e:
            logger.error("Failed to search users", error=str(e), query=query)
            raise
    
    def update_user(self, user: User) -> User:
        """Update an existing user."""
        try:
            # Validate user data
            errors = user.validate()
            if errors:
                raise ValueError(f"User validation failed: {', '.join(errors)}")
            
            # Check if username or email conflicts with other users
            existing_user = self.get_user_by_username(user.username)
            if existing_user and existing_user.id != user.id:
                raise ValueError("Username already exists")
            
            existing_user = self.get_user_by_email(user.email)
            if existing_user and existing_user.id != user.id:
                raise ValueError("Email already exists")
            
            # Update timestamps
            user.updated_at = datetime.now(timezone.utc)
            
            # Update user in database
            query = """
                UPDATE users SET
                    username = %s, email = %s, password_hash = %s, salt = %s,
                    first_name = %s, last_name = %s, role = %s, is_active = %s,
                    is_verified = %s, last_login = %s, permissions = %s,
                    api_key = %s, api_key_created = %s, updated_at = %s
                WHERE id = %s
            """
            
            import json
            params = (
                user.username, user.email, user.password_hash, user.salt,
                user.first_name, user.last_name, user.role, user.is_active,
                user.is_verified, user.last_login, json.dumps(user.permissions),
                user.api_key, user.api_key_created, user.updated_at, user.id
            )
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, params)
                if cursor.rowcount == 0:
                    raise ValueError("User not found")
                cursor.connection.commit()
            
            logger.info("User updated successfully", user_id=user.id, username=user.username)
            return user
            
        except Exception as e:
            logger.error("Failed to update user", error=str(e), user_id=user.id)
            raise
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user (soft delete by setting is_active = false)."""
        try:
            query = "UPDATE users SET is_active = false, updated_at = %s WHERE id = %s"
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (datetime.now(timezone.utc), user_id))
                if cursor.rowcount == 0:
                    logger.warning("User not found for deletion", user_id=user_id)
                    return False
                cursor.connection.commit()
            
            logger.info("User deactivated successfully", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Failed to delete user", error=str(e), user_id=user_id)
            raise
    
    def hard_delete_user(self, user_id: int) -> bool:
        """Permanently delete a user from the database."""
        try:
            query = "DELETE FROM users WHERE id = %s"
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                if cursor.rowcount == 0:
                    logger.warning("User not found for hard deletion", user_id=user_id)
                    return False
                cursor.connection.commit()
            
            logger.info("User permanently deleted", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Failed to hard delete user", error=str(e), user_id=user_id)
            raise
    
    def update_user_password(self, user_id: int, new_password: str) -> bool:
        """Update a user's password."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            user.set_password(new_password)
            user.updated_at = datetime.now(timezone.utc)
            
            query = "UPDATE users SET password_hash = %s, salt = %s, updated_at = %s WHERE id = %s"
            params = (user.password_hash, user.salt, user.updated_at, user_id)
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, params)
                cursor.connection.commit()
            
            logger.info("User password updated", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Failed to update user password", error=str(e), user_id=user_id)
            raise
    
    def update_user_role(self, user_id: int, new_role: str) -> bool:
        """Update a user's role and permissions."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            user.update_role(new_role)
            user.updated_at = datetime.now(timezone.utc)
            
            query = "UPDATE users SET role = %s, permissions = %s, updated_at = %s WHERE id = %s"
            import json
            params = (user.role, json.dumps(user.permissions), user.updated_at, user_id)
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, params)
                cursor.connection.commit()
            
            logger.info("User role updated", user_id=user_id, new_role=new_role)
            return True
            
        except Exception as e:
            logger.error("Failed to update user role", error=str(e), user_id=user_id)
            raise
    
    def regenerate_api_key(self, user_id: int) -> str:
        """Regenerate a user's API key."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            new_api_key = user.generate_api_key()
            user.updated_at = datetime.now(timezone.utc)
            
            query = "UPDATE users SET api_key = %s, api_key_created = %s, updated_at = %s WHERE id = %s"
            params = (user.api_key, user.api_key_created, user.updated_at, user_id)
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, params)
                cursor.connection.commit()
            
            logger.info("API key regenerated", user_id=user_id)
            return new_api_key
            
        except Exception as e:
            logger.error("Failed to regenerate API key", error=str(e), user_id=user_id)
            raise
    
    def revoke_api_key(self, user_id: int) -> bool:
        """Revoke a user's API key."""
        try:
            query = "UPDATE users SET api_key = NULL, api_key_created = NULL, updated_at = %s WHERE id = %s"
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (datetime.now(timezone.utc), user_id))
                cursor.connection.commit()
            
            logger.info("API key revoked", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Failed to revoke API key", error=str(e), user_id=user_id)
            raise
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        try:
            query = "UPDATE users SET last_login = %s WHERE id = %s"
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (datetime.now(timezone.utc), user_id))
                cursor.connection.commit()
            
            logger.info("Last login updated", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Failed to update last login", error=str(e), user_id=user_id)
            raise
    
    def get_user_count(self, active_only: bool = True) -> int:
        """Get the total number of users."""
        try:
            query = "SELECT COUNT(*) FROM users"
            if active_only:
                query += " WHERE is_active = true"
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                
                logger.info("User count retrieved", count=count, active_only=active_only)
                return count
                
        except Exception as e:
            logger.error("Failed to get user count", error=str(e))
            raise
    
    def get_users_by_role(self, role: str) -> List[User]:
        """Get all users with a specific role."""
        try:
            query = "SELECT * FROM users WHERE role = %s AND is_active = true ORDER BY username"
            
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (role,))
                rows = cursor.fetchall()
                
                users = [User.from_database_row(dict(row)) for row in rows]
                logger.info("Users retrieved by role", role=role, count=len(users))
                return users
                
        except Exception as e:
            logger.error("Failed to get users by role", error=str(e), role=role)
            raise
