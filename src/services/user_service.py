"""UserService for user authentication in the todo chatbot application."""

import logging
from typing import Optional, Dict, Any
import hashlib
import secrets
import uuid as uuid_mod

from src.models.user import User, AuthenticatedUser
from src.utils.database import db_pool
from src.utils.helpers import is_valid_uuid, get_current_iso_timestamp, get_current_datetime, validate_email
from src.config.jwt_config import JWTConfig

try:
    import jwt
except ImportError:
    jwt = None


class UserService:
    """Service class for user authentication and management."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """Hash a password with a salt using SHA-256."""
        if salt is None:
            salt = secrets.token_hex(16)
        hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return f"{salt}:{hashed}", salt

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify a password against its stored hash."""
        if ':' not in stored_hash:
            return False
        salt, _ = stored_hash.split(':', 1)
        computed_hash, _ = self._hash_password(password, salt)
        return computed_hash == stored_hash

    def _generate_token(self, user_id: str, username: str, token_type: str = "access") -> str:
        """Generate a JWT token for the user."""
        if jwt is None:
            raise RuntimeError("PyJWT is required for token generation")

        from datetime import datetime, timezone

        if token_type == "access":
            expiry = JWTConfig.get_access_token_expiry()
        else:
            expiry = JWTConfig.get_refresh_token_expiry()

        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "username": username,
            "type": token_type,
            "iat": now,
            "exp": now + expiry,
        }
        return jwt.encode(payload, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        if jwt is None:
            raise RuntimeError("PyJWT is required for token verification")

        try:
            payload = jwt.decode(
                token,
                JWTConfig.SECRET_KEY,
                algorithms=[JWTConfig.ALGORITHM],
            )
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None

    async def register_user(self, username: str, email: str, password: str) -> AuthenticatedUser:
        """Register a new user."""
        try:
            if not username or len(username.strip()) < 3:
                raise ValueError("Username must be at least 3 characters")

            if not validate_email(email):
                raise ValueError("Invalid email format")

            if not password or len(password) < 8:
                raise ValueError("Password must be at least 8 characters")

            hashed_password, _ = self._hash_password(password)
            now = get_current_datetime()

            query = """
                INSERT INTO users (username, email, hashed_password, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING user_id, username, email, created_at, updated_at, preferences
            """

            async with db_pool.get_db_connection() as conn:
                result = await conn.fetchrow(query, username, email, hashed_password, now, now)

            user = AuthenticatedUser(
                userId=str(result['user_id']),
                username=result['username'],
                email=result['email'],
                createdAt=result['created_at'] if isinstance(result['created_at'], str) else result['created_at'].isoformat() + 'Z',
                updatedAt=result['updated_at'] if isinstance(result['updated_at'], str) else result['updated_at'].isoformat() + 'Z',
                preferences=result['preferences'] or {},
                hashed_password=hashed_password,
                is_active=True,
            )

            self.logger.info(f"User registered successfully: {user.userId}")
            return user

        except Exception as e:
            self.logger.error(f"Error registering user: {e}")
            raise

    async def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user and return tokens."""
        try:
            query = """
                SELECT user_id, username, email, hashed_password, is_active,
                       created_at, updated_at, preferences, last_login_at
                FROM users
                WHERE email = $1
            """

            async with db_pool.get_db_connection() as conn:
                result = await conn.fetchrow(query, email)

            if not result:
                self.logger.warning(f"Authentication failed: user not found for email {email}")
                return None

            stored_hash = result['hashed_password']
            if not stored_hash or not self._verify_password(password, stored_hash):
                self.logger.warning(f"Authentication failed: invalid password for email {email}")
                return None

            if not result.get('is_active', True):
                self.logger.warning(f"Authentication failed: user inactive for email {email}")
                return None

            user_id = str(result['user_id'])
            username = result['username']

            # Update last login
            update_query = "UPDATE users SET last_login_at = $1 WHERE user_id = $2"
            now = get_current_datetime()
            async with db_pool.get_db_connection() as conn:
                await conn.execute(update_query, now, result['user_id'])

            access_token = self._generate_token(user_id, username, "access")
            refresh_token = self._generate_token(user_id, username, "refresh")

            self.logger.info(f"User authenticated successfully: {user_id}")
            return {
                "accessToken": access_token,
                "refreshToken": refresh_token,
                "user": {
                    "userId": user_id,
                    "username": username,
                    "email": result['email'],
                },
            }

        except Exception as e:
            self.logger.error(f"Error authenticating user: {e}")
            raise

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID."""
        try:
            if not is_valid_uuid(user_id):
                raise ValueError("Invalid user ID format")

            query = """
                SELECT user_id, username, email, created_at, updated_at, preferences
                FROM users WHERE user_id = $1
            """

            async with db_pool.get_db_connection() as conn:
                result = await conn.fetchrow(query, uuid_mod.UUID(user_id))

            if not result:
                return None

            return User(
                userId=str(result['user_id']),
                username=result['username'],
                email=result['email'],
                createdAt=result['created_at'].isoformat() + 'Z' if hasattr(result['created_at'], 'isoformat') else result['created_at'],
                updatedAt=result['updated_at'].isoformat() + 'Z' if hasattr(result['updated_at'], 'isoformat') else result['updated_at'],
                preferences=result['preferences'] or {},
            )

        except Exception as e:
            self.logger.error(f"Error getting user {user_id}: {e}")
            raise

    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """Update a user's profile."""
        try:
            if not is_valid_uuid(user_id):
                raise ValueError("Invalid user ID format")

            current_user = await self.get_user_by_id(user_id)
            if not current_user:
                return None

            username = update_data.get('username', current_user.username)
            email = update_data.get('email', current_user.email)
            preferences = update_data.get('preferences', current_user.preferences)
            now = get_current_datetime()

            query = """
                UPDATE users SET username = $1, email = $2, preferences = $3, updated_at = $4
                WHERE user_id = $5
                RETURNING user_id, username, email, created_at, updated_at, preferences
            """

            import json
            prefs_json = json.dumps(preferences) if preferences else None
            async with db_pool.get_db_connection() as conn:
                result = await conn.fetchrow(query, username, email, prefs_json, now, uuid_mod.UUID(user_id))

            if not result:
                return None

            return User(
                userId=str(result['user_id']),
                username=result['username'],
                email=result['email'],
                createdAt=result['created_at'].isoformat() + 'Z' if hasattr(result['created_at'], 'isoformat') else result['created_at'],
                updatedAt=result['updated_at'].isoformat() + 'Z' if hasattr(result['updated_at'], 'isoformat') else result['updated_at'],
                preferences=result['preferences'] or {},
            )

        except Exception as e:
            self.logger.error(f"Error updating user profile {user_id}: {e}")
            raise

    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh an access token using a refresh token."""
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        user_id = payload["sub"]
        username = payload["username"]
        new_access_token = self._generate_token(user_id, username, "access")
        return {"accessToken": new_access_token}
