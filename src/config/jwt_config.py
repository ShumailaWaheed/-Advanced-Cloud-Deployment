import os
from datetime import timedelta

class JWTConfig:
    """JWT Configuration settings"""

    # JWT Secret - should be stored in secrets
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-default-dev-secret-key-change-in-production')

    # Token expiration
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))

    # Algorithm
    ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

    @classmethod
    def get_access_token_expiry(cls):
        return timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)

    @classmethod
    def get_refresh_token_expiry(cls):
        return timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)