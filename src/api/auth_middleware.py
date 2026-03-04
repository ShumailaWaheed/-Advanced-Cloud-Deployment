"""Authentication middleware for FastAPI endpoints."""

import logging
from typing import Optional

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.services.user_service import UserService

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)
_user_service = UserService()


async def get_current_user_id(request: Request) -> str:
    """Extract and validate the current user ID from the JWT token.

    Reads the Authorization header, verifies the token, and returns
    the user ID (``sub`` claim).  Raises 401 if the token is missing
    or invalid.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ", 1)[1]
    payload = _user_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
