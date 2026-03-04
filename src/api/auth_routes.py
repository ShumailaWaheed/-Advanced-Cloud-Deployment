"""Authentication API routes for the todo chatbot application."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from src.api.auth_middleware import get_current_user_id
from src.services.user_service import UserService
from src.services.task_event_service import TaskEventService
from src.utils.constants import EventType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

user_service = UserService()
event_service = TaskEventService()


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: str
    password: str


class UpdateProfileRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = None
    preferences: Optional[dict] = None


class RefreshTokenRequest(BaseModel):
    refreshToken: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    """POST /api/v1/auth/register - Register a new user."""
    try:
        user = await user_service.register_user(body.username, body.email, body.password)

        # Publish user.created event (T088)
        await event_service.publish_user_event(
            EventType.USER_CREATED,
            user.to_dict(),
        )

        return user.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=409, detail="Username or email already exists")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login")
async def login(body: LoginRequest):
    """POST /api/v1/auth/login - Authenticate and get tokens."""
    try:
        result = await user_service.authenticate(body.email, body.password)
        if not result:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/profile")
async def get_profile(user_id: str = Depends(get_current_user_id)):
    """GET /api/v1/auth/profile - Get the current user's profile."""
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/profile")
async def update_profile(
    body: UpdateProfileRequest,
    user_id: str = Depends(get_current_user_id),
):
    """PUT /api/v1/auth/profile - Update the current user's profile."""
    try:
        update_data = {k: v for k, v in body.model_dump().items() if v is not None}
        user = await user_service.update_user_profile(user_id, update_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Publish user.profile.updated event (T089)
        await event_service.publish_user_event(
            EventType.USER_PROFILE_UPDATED,
            user.to_dict(),
        )

        return user.to_dict()
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh")
async def refresh_token(body: RefreshTokenRequest):
    """POST /api/v1/auth/refresh - Refresh an access token."""
    try:
        result = await user_service.refresh_access_token(body.refreshToken)
        if not result:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refresh token error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
