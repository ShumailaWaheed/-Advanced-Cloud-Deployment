"""Recurring Task API routes for the todo chatbot application."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.auth_middleware import get_current_user_id
from src.services.recurring_task_service import RecurringTaskService
from src.services.task_event_service import TaskEventService
from src.models.recurring_task import RecurringTask, RecurrencePattern
from src.utils.constants import EventType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/recurring-tasks", tags=["recurring-tasks"])

recurring_service = RecurringTaskService()
event_service = TaskEventService()


class PatternRequest(BaseModel):
    type: str = "DAILY"
    interval: int = 1
    daysOfWeek: Optional[List[int]] = None
    dayOfMonth: Optional[int] = None
    month: Optional[int] = None
    startTime: Optional[str] = None


class CreateRecurringTaskRequest(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: str = "MEDIUM"
    pattern: PatternRequest
    isActive: bool = True
    endDate: Optional[str] = None


class UpdateRecurringTaskRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = None
    pattern: Optional[PatternRequest] = None
    isActive: Optional[bool] = None
    endDate: Optional[str] = None


@router.get("")
async def get_recurring_tasks(user_id: str = Depends(get_current_user_id)):
    """GET /api/v1/recurring-tasks"""
    try:
        tasks = await recurring_service.get_recurring_tasks_by_user(user_id)
        return {"recurringTasks": [t.to_dict() for t in tasks]}
    except Exception as e:
        logger.error(f"Error listing recurring tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_recurring_task(body: CreateRecurringTaskRequest, user_id: str = Depends(get_current_user_id)):
    """POST /api/v1/recurring-tasks"""
    try:
        pattern = RecurrencePattern(
            type=body.pattern.type,
            interval=body.pattern.interval,
            daysOfWeek=body.pattern.daysOfWeek,
            dayOfMonth=body.pattern.dayOfMonth,
            month=body.pattern.month,
            startTime=body.pattern.startTime,
        )
        rt = RecurringTask(
            userId=user_id,
            title=body.title,
            description=body.description,
            priority=body.priority,
            pattern=pattern,
            isActive=body.isActive,
            endDate=body.endDate,
        )
        created = await recurring_service.create_recurring_task(rt)

        # Publish recurring-task.created event
        await event_service.publish_user_event(EventType.RECURRING_TASK_CREATED, created.to_dict())

        return created.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating recurring task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{task_id}")
async def update_recurring_task(task_id: str, body: UpdateRecurringTaskRequest, user_id: str = Depends(get_current_user_id)):
    """PUT /api/v1/recurring-tasks/{taskId}"""
    try:
        update_data = {k: v for k, v in body.model_dump().items() if v is not None}
        if "pattern" in update_data and update_data["pattern"]:
            update_data["pattern"] = update_data["pattern"]
        updated = await recurring_service.update_recurring_task(task_id, user_id, update_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Recurring task not found")
        return updated.to_dict()
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating recurring task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_task(task_id: str, user_id: str = Depends(get_current_user_id)):
    """DELETE /api/v1/recurring-tasks/{taskId}"""
    try:
        deleted = await recurring_service.delete_recurring_task(task_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Recurring task not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting recurring task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
