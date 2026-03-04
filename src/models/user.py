"""User entity model for the todo chatbot application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
import uuid
import re
from src.utils.helpers import is_valid_uuid, get_current_iso_timestamp, validate_email


@dataclass
class User:
    """User entity representing a system user with authentication and preferences."""

    # Core fields
    userId: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""

    # Optional fields
    createdAt: str = field(default_factory=get_current_iso_timestamp)
    updatedAt: str = field(default_factory=get_current_iso_timestamp)
    preferences: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate the user after initialization."""
        self.validate()

        # Ensure userId is a valid UUID string
        if not self.userId or not is_valid_uuid(self.userId):
            self.userId = str(uuid.uuid4())

    def validate(self):
        """Validate the user data."""
        # Validate username
        if not self.username or len(self.username.strip()) == 0:
            raise ValueError("Username is required")

        if len(self.username) < 3 or len(self.username) > 50:
            raise ValueError("Username must be between 3 and 50 characters")

        if not re.match(r'^[a-zA-Z0-9_-]+$', self.username):
            raise ValueError("Username can only contain alphanumeric characters, underscores, and hyphens")

        # Validate email
        if not self.email or len(self.email.strip()) == 0:
            raise ValueError("Email is required")

        if not validate_email(self.email):
            raise ValueError("Email must be a valid email address")

        # Check if preferences is a dictionary if provided
        if self.preferences is not None and not isinstance(self.preferences, dict):
            raise ValueError("Preferences must be a dictionary or None")

    def update_username(self, new_username: str):
        """Update the user's username."""
        if not new_username or len(new_username.strip()) == 0:
            raise ValueError("Username cannot be empty")

        if len(new_username) < 3 or len(new_username) > 50:
            raise ValueError("Username must be between 3 and 50 characters")

        if not re.match(r'^[a-zA-Z0-9_-]+$', new_username):
            raise ValueError("Username can only contain alphanumeric characters, underscores, and hyphens")

        self.username = new_username
        self.updatedAt = get_current_iso_timestamp()

    def update_email(self, new_email: str):
        """Update the user's email."""
        if not new_email or len(new_email.strip()) == 0:
            raise ValueError("Email cannot be empty")

        if not validate_email(new_email):
            raise ValueError("Email must be a valid email address")

        self.email = new_email
        self.updatedAt = get_current_iso_timestamp()

    def update_preferences(self, new_preferences: Dict[str, Any]):
        """Update the user's preferences."""
        if not isinstance(new_preferences, dict):
            raise ValueError("Preferences must be a dictionary")

        self.preferences = new_preferences
        self.updatedAt = get_current_iso_timestamp()

    def add_preference(self, key: str, value: Any):
        """Add or update a single preference."""
        if self.preferences is None:
            self.preferences = {}

        self.preferences[key] = value
        self.updatedAt = get_current_iso_timestamp()

    def remove_preference(self, key: str):
        """Remove a preference."""
        if self.preferences and key in self.preferences:
            del self.preferences[key]
            self.updatedAt = get_current_iso_timestamp()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the user to a dictionary."""
        return {
            "userId": self.userId,
            "username": self.username,
            "email": self.email,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
            "preferences": self.preferences
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User instance from a dictionary."""
        return cls(
            userId=data.get('userId', ''),
            username=data.get('username', ''),
            email=data.get('email', ''),
            createdAt=data.get('createdAt', get_current_iso_timestamp()),
            updatedAt=data.get('updatedAt', get_current_iso_timestamp()),
            preferences=data.get('preferences', {})
        )


@dataclass
class AuthenticatedUser(User):
    """Extended User entity with authentication-specific fields."""

    hashed_password: str = ""
    is_active: bool = True
    last_login_at: Optional[str] = None

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login_at = get_current_iso_timestamp()
        self.updatedAt = get_current_iso_timestamp()

    def deactivate(self):
        """Deactivate the user account."""
        self.is_active = False
        self.updatedAt = get_current_iso_timestamp()

    def activate(self):
        """Activate the user account."""
        self.is_active = True
        self.updatedAt = get_current_iso_timestamp()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the authenticated user to a dictionary (excluding sensitive data)."""
        base_dict = super().to_dict()
        # Exclude sensitive information like hashed password
        base_dict.update({
            "isActive": self.is_active,
            "lastLoginAt": self.last_login_at
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthenticatedUser':
        """Create an AuthenticatedUser instance from a dictionary."""
        return cls(
            userId=data.get('userId', ''),
            username=data.get('username', ''),
            email=data.get('email', ''),
            createdAt=data.get('createdAt', get_current_iso_timestamp()),
            updatedAt=data.get('updatedAt', get_current_iso_timestamp()),
            preferences=data.get('preferences', {}),
            hashed_password=data.get('hashedPassword', ''),
            is_active=data.get('isActive', True),
            last_login_at=data.get('lastLoginAt')
        )