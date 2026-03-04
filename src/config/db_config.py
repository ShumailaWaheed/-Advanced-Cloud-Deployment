"""Database configuration for the todo chatbot application."""

import os
from typing import Optional


class DatabaseConfig:
    """Database configuration settings."""

    # Full DSN override (e.g. for Neon)
    DATABASE_URL = os.getenv('DATABASE_URL', '')

    # Database connection parameters
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '5432'))
    DB_NAME = os.getenv('DB_NAME', 'todochatbot')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'example')

    # Connection pool settings
    DB_POOL_MIN_SIZE = int(os.getenv('DB_POOL_MIN_SIZE', '1'))
    DB_POOL_MAX_SIZE = int(os.getenv('DB_POOL_MAX_SIZE', '10'))
    DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '30'))
    DB_POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '3600'))  # 1 hour

    # Connection timeout settings
    DB_CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', '10'))
    DB_STATEMENT_TIMEOUT = int(os.getenv('DB_STATEMENT_TIMEOUT', '30'))

    # SSL settings
    DB_SSL_MODE = os.getenv('DB_SSL_MODE', 'prefer')  # disable, allow, prefer, require, verify-ca, verify-full

    @classmethod
    def get_database_url(cls) -> str:
        """Get the database connection URL."""
        # Read at call time so dotenv has a chance to load first
        db_url = os.getenv('DATABASE_URL', '')
        if db_url:
            return db_url
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    @classmethod
    def get_async_database_url(cls) -> str:
        """Get the async database connection URL for async engines."""
        return f"postgresql+asyncpg://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    @classmethod
    def get_sync_database_url(cls) -> str:
        """Get the sync database connection URL for sync operations."""
        return f"postgresql+psycopg2://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    @classmethod
    def get_dapr_state_store_config(cls) -> dict:
        """Get Dapr state store configuration."""
        return {
            "connection_string": cls.get_database_url(),
            "table": "state",
            "actorStateStore": True
        }

    @classmethod
    def validate_config(cls) -> bool:
        """Validate database configuration."""
        if not cls.DB_HOST:
            raise ValueError("DB_HOST is required")

        if cls.DB_PORT <= 0 or cls.DB_PORT > 65535:
            raise ValueError("DB_PORT must be between 1 and 65535")

        if not cls.DB_NAME:
            raise ValueError("DB_NAME is required")

        if not cls.DB_USER:
            raise ValueError("DB_USER is required")

        if cls.DB_POOL_MIN_SIZE < 0:
            raise ValueError("DB_POOL_MIN_SIZE must be >= 0")

        if cls.DB_POOL_MAX_SIZE <= 0:
            raise ValueError("DB_POOL_MAX_SIZE must be > 0")

        if cls.DB_POOL_MIN_SIZE > cls.DB_POOL_MAX_SIZE:
            raise ValueError("DB_POOL_MIN_SIZE cannot be greater than DB_POOL_MAX_SIZE")

        return True