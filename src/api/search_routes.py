"""Search API routes for the todo chatbot application."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.auth_middleware import get_current_user_id
from src.services.search_service import SearchService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tasks/search", tags=["search"])

search_service = SearchService()


@router.get("")
async def search_tasks(
    q: Optional[str] = Query(None, description="Full-text search query"),
    tag: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sortBy: Optional[str] = Query("createdAt"),
    sortOrder: Optional[str] = Query("desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """GET /api/v1/tasks/search - Search, filter, and sort tasks."""
    try:
        results = await search_service.search_tasks(
            user_id=user_id,
            query=q,
            tag=tag,
            priority=priority,
            status=status,
            sort_by=sortBy,
            sort_order=sortOrder,
            page=page,
            limit=limit,
        )
        return results
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
