"""Task API routes for the todo chatbot application."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.api.auth_middleware import get_current_user_id
from src.services.task_service import TaskService
from src.services.task_event_service import TaskEventService
from src.services.validation import TaskValidator, ValidationError
from src.models.task import Task
from src.utils.constants import TaskPriority, TaskStatus, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from src.utils.database import db_pool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

task_service = TaskService()
event_service = TaskEventService()


# --- Pydantic request/response models ---

class CreateTaskRequest(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    dueDate: Optional[str] = None
    priority: Optional[str] = Field("MEDIUM")
    status: Optional[str] = Field("TO_DO")
    tags: Optional[List[str]] = None
    recurrencePattern: Optional[dict] = None


class UpdateTaskRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    dueDate: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None


class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    totalPages: int


class TaskResponse(BaseModel):
    taskId: str
    userId: str
    title: str
    description: Optional[str] = None
    dueDate: Optional[str] = None
    priority: str
    status: str
    tags: List[str] = []
    createdAt: str
    updatedAt: str
    completedAt: Optional[str] = None
    recurrencePattern: Optional[dict] = None


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    pagination: PaginationResponse


# --- Helper functions ---

def _task_to_response(task: Task) -> dict:
    """Convert a Task model to a response dict."""
    d = task.to_dict()
    # Normalise enum values
    if hasattr(d.get("priority"), "value"):
        d["priority"] = d["priority"].value
    if hasattr(d.get("status"), "value"):
        d["status"] = d["status"].value
    return d


# --- Endpoints ---

@router.get("", response_model=TaskListResponse)
async def get_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sortBy: Optional[str] = Query(None),
    sortOrder: Optional[str] = Query("asc"),
    user_id: str = Depends(get_current_user_id),
):
    """GET /api/v1/tasks - List tasks for the authenticated user."""
    try:
        offset = (page - 1) * limit
        tasks = await task_service.get_tasks_by_user(user_id, limit=limit, offset=offset)

        # Get total count for pagination
        count_query = "SELECT COUNT(*) FROM tasks WHERE user_id = $1"
        async with db_pool.get_db_connection() as conn:
            total = await conn.fetchval(count_query, user_id)

        total_pages = (total + limit - 1) // limit if total else 0
        task_dicts = [_task_to_response(t) for t in tasks]

        return {
            "tasks": task_dicts,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": total_pages,
            },
        }
    except Exception as e:
        import traceback
        logger.error(f"Error listing tasks: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: CreateTaskRequest,
    user_id: str = Depends(get_current_user_id),
):
    """POST /api/v1/tasks - Create a new task."""
    try:
        validated = TaskValidator.validate_create_task(body.model_dump())

        task = Task(
            userId=user_id,
            title=validated["title"],
            description=validated["description"],
            dueDate=validated["dueDate"],
            priority=TaskPriority(validated["priority"]),
            status=TaskStatus(validated["status"]),
            tags=validated["tags"],
            recurrencePattern=body.recurrencePattern,
        )

        created = await task_service.create_task(task)

        # Publish event (T027)
        await event_service.publish_task_created(created)

        return _task_to_response(created)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """GET /api/v1/tasks/{taskId} - Get a specific task."""
    try:
        task = await task_service.get_task_by_id(task_id, user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return _task_to_response(task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    body: UpdateTaskRequest,
    user_id: str = Depends(get_current_user_id),
):
    """PUT /api/v1/tasks/{taskId} - Update a task."""
    try:
        raw = {k: v for k, v in body.model_dump().items() if v is not None}
        validated = TaskValidator.validate_update_task(raw)

        # Capture previous state for event
        previous_task = await task_service.get_task_by_id(task_id, user_id)
        if not previous_task:
            raise HTTPException(status_code=404, detail="Task not found")
        previous_data = previous_task.to_dict()

        updated = await task_service.update_task(task_id, user_id, validated)
        if not updated:
            raise HTTPException(status_code=404, detail="Task not found")

        # Publish appropriate events (T028, T031, T032)
        await event_service.publish_task_updated(updated, previous_data)

        if "priority" in validated and validated["priority"] != previous_data.get("priority"):
            await event_service.publish_task_priority_changed(updated, previous_data)

        if "dueDate" in validated and validated["dueDate"] != previous_data.get("dueDate"):
            await event_service.publish_task_due_date_changed(updated, previous_data)

        if "status" in validated and validated["status"] == TaskStatus.DONE.value:
            await event_service.publish_task_completed(updated, previous_data)

        return _task_to_response(updated)
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """DELETE /api/v1/tasks/{taskId} - Delete a task."""
    try:
        # Get task before deletion for event
        task = await task_service.get_task_by_id(task_id, user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        deleted = await task_service.delete_task(task_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Task not found")

        # Publish event (T029)
        await event_service.publish_task_deleted(task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
