"""TaskService for managing task CRUD operations in the todo chatbot application."""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from uuid import UUID
import uuid

from src.models.task import Task
from src.models.task_event import TaskEvent
from src.utils.database import db_pool
from src.utils.constants import TaskPriority, TaskStatus, EventType
from src.utils.helpers import is_valid_uuid, get_current_iso_timestamp
from src.config.db_config import DatabaseConfig
from datetime import datetime, timezone
import json as json_mod


def _parse_dt(val):
    """Convert a string timestamp to datetime, or return None."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    s = val.rstrip('Z')
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _dt_to_str(val):
    """Convert a datetime to ISO string, or return None."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.isoformat().replace('+00:00', 'Z')
    return str(val)


def _row_to_task(result) -> Task:
    """Convert a DB row to a Task object."""
    return Task(
        taskId=str(result['task_id']),
        userId=str(result['user_id']),
        title=result['title'],
        description=result['description'],
        dueDate=_dt_to_str(result['due_date']),
        priority=TaskPriority(result['priority']),
        status=TaskStatus(result['status']),
        tags=result['tags'] if result['tags'] else [],
        createdAt=_dt_to_str(result['created_at']),
        updatedAt=_dt_to_str(result['updated_at']),
        completedAt=_dt_to_str(result['completed_at']),
        recurrencePattern=result['recurrence_pattern'],
    )


class TaskService:
    """Service class for managing task operations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def create_task(self, task: Task) -> Task:
        """Create a new task."""
        try:
            # Validate task
            task.validate()

            # Insert task into database — let DB handle created_at/updated_at defaults
            query = """
                INSERT INTO tasks (task_id, user_id, title, description, due_date, priority, status, tags, recurrence_pattern)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING task_id, user_id, title, description, due_date, priority, status, tags, created_at, updated_at, completed_at, recurrence_pattern
            """

            # Convert priority and status to string values
            priority_value = task.priority.value if hasattr(task.priority, 'value') else str(task.priority)
            status_value = task.status.value if hasattr(task.status, 'value') else str(task.status)
            recurrence_json = json_mod.dumps(task.recurrencePattern) if task.recurrencePattern else None

            async with db_pool.get_db_connection() as conn:
                result = await conn.fetchrow(
                    query,
                    task.taskId,
                    task.userId,
                    task.title,
                    task.description,
                    _parse_dt(task.dueDate),
                    priority_value,
                    status_value,
                    task.tags,
                    recurrence_json,
                )

            created_task = _row_to_task(result)
            self.logger.info(f"Task created successfully: {created_task.taskId}")
            return created_task

        except Exception as e:
            self.logger.error(f"Error creating task: {e}")
            raise

    async def get_task_by_id(self, task_id: str, user_id: str) -> Optional[Task]:
        """Get a task by its ID for a specific user."""
        try:
            if not is_valid_uuid(task_id):
                raise ValueError("Invalid task ID format")

            if not is_valid_uuid(user_id):
                raise ValueError("Invalid user ID format")

            query = """
                SELECT task_id, user_id, title, description, due_date, priority, status, tags, created_at, updated_at, completed_at, recurrence_pattern
                FROM tasks
                WHERE task_id = $1 AND user_id = $2
            """

            async with db_pool.get_db_connection() as conn:
                result = await conn.fetchrow(query, task_id, user_id)

            if not result:
                return None

            return _row_to_task(result)

        except Exception as e:
            self.logger.error(f"Error retrieving task {task_id}: {e}")
            raise

    async def get_tasks_by_user(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Task]:
        """Get all tasks for a specific user with pagination."""
        try:
            if not is_valid_uuid(user_id):
                raise ValueError("Invalid user ID format")

            query = """
                SELECT task_id, user_id, title, description, due_date, priority, status, tags, created_at, updated_at, completed_at, recurrence_pattern
                FROM tasks
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            """

            async with db_pool.get_db_connection() as conn:
                results = await conn.fetch(query, user_id, limit, offset)

            tasks = []
            for result in results:
                task = _row_to_task(result
                )
                tasks.append(task)

            return tasks

        except Exception as e:
            self.logger.error(f"Error retrieving tasks for user {user_id}: {e}")
            raise

    async def update_task(self, task_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Task]:
        """Update an existing task."""
        try:
            if not is_valid_uuid(task_id):
                raise ValueError("Invalid task ID format")

            if not is_valid_uuid(user_id):
                raise ValueError("Invalid user ID format")

            # Get current task to update
            current_task = await self.get_task_by_id(task_id, user_id)
            if not current_task:
                return None

            # Apply updates
            for key, value in update_data.items():
                if hasattr(current_task, key):
                    if key == 'priority' and isinstance(value, str):
                        setattr(current_task, key, TaskPriority(value.upper()))
                    elif key == 'status' and isinstance(value, str):
                        setattr(current_task, key, TaskStatus(value.upper()))
                    elif key in ['tags'] and isinstance(value, list):
                        setattr(current_task, key, value)
                    elif key in ['title', 'description']:
                        setattr(current_task, key, value)
                    elif key == 'dueDate':
                        setattr(current_task, key, value)
                    elif key == 'recurrencePattern':
                        setattr(current_task, key, value)

            # Validate updated task
            current_task.validate()
            current_task.updatedAt = get_current_iso_timestamp()

            # Update in database
            query = """
                UPDATE tasks
                SET title = $1, description = $2, due_date = $3, priority = $4, status = $5,
                    tags = $6, updated_at = $7, completed_at = $8, recurrence_pattern = $9
                WHERE task_id = $10 AND user_id = $11
                RETURNING task_id, user_id, title, description, due_date, priority, status, tags, created_at, updated_at, completed_at, recurrence_pattern
            """

            priority_value = current_task.priority.value if hasattr(current_task.priority, 'value') else str(current_task.priority)
            status_value = current_task.status.value if hasattr(current_task.status, 'value') else str(current_task.status)

            recurrence_json = json_mod.dumps(current_task.recurrencePattern) if current_task.recurrencePattern else None

            async with db_pool.get_db_connection() as conn:
                result = await conn.fetchrow(
                    query,
                    current_task.title,
                    current_task.description,
                    _parse_dt(current_task.dueDate),
                    priority_value,
                    status_value,
                    current_task.tags,
                    datetime.now(timezone.utc),
                    _parse_dt(current_task.completedAt),
                    recurrence_json,
                    current_task.taskId,
                    current_task.userId
                )

            if not result:
                return None

            updated_task = _row_to_task(result)
            self.logger.info(f"Task updated successfully: {updated_task.taskId}")
            return updated_task

        except Exception as e:
            self.logger.error(f"Error updating task {task_id}: {e}")
            raise

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete a task by its ID for a specific user."""
        try:
            if not is_valid_uuid(task_id):
                raise ValueError("Invalid task ID format")

            if not is_valid_uuid(user_id):
                raise ValueError("Invalid user ID format")

            query = """
                DELETE FROM tasks
                WHERE task_id = $1 AND user_id = $2
                RETURNING task_id
            """

            async with db_pool.get_db_connection() as conn:
                result = await conn.fetchrow(query, task_id, user_id)

            if result:
                self.logger.info(f"Task deleted successfully: {task_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error deleting task {task_id}: {e}")
            raise

    async def complete_task(self, task_id: str, user_id: str) -> Optional[Task]:
        """Mark a task as completed."""
        try:
            update_data = {
                'status': TaskStatus.DONE.value,
                'completedAt': get_current_iso_timestamp()
            }
            return await self.update_task(task_id, user_id, update_data)
        except Exception as e:
            self.logger.error(f"Error completing task {task_id}: {e}")
            raise

    async def get_tasks_by_status(self, user_id: str, status: TaskStatus, limit: int = 20, offset: int = 0) -> List[Task]:
        """Get tasks by status for a specific user."""
        try:
            if not is_valid_uuid(user_id):
                raise ValueError("Invalid user ID format")

            status_value = status.value if hasattr(status, 'value') else str(status)

            query = """
                SELECT task_id, user_id, title, description, due_date, priority, status, tags, created_at, updated_at, completed_at, recurrence_pattern
                FROM tasks
                WHERE user_id = $1 AND status = $2
                ORDER BY created_at DESC
                LIMIT $3 OFFSET $4
            """

            async with db_pool.get_db_connection() as conn:
                results = await conn.fetch(query, user_id, status_value, limit, offset)

            tasks = [_row_to_task(r) for r in results]

            return tasks

        except Exception as e:
            self.logger.error(f"Error retrieving tasks by status {status} for user {user_id}: {e}")
            raise

    async def get_overdue_tasks(self, user_id: str) -> List[Task]:
        """Get all overdue tasks for a specific user."""
        try:
            if not is_valid_uuid(user_id):
                raise ValueError("Invalid user ID format")

            query = """
                SELECT task_id, user_id, title, description, due_date, priority, status, tags, created_at, updated_at, completed_at, recurrence_pattern
                FROM tasks
                WHERE user_id = $1
                  AND due_date IS NOT NULL
                  AND due_date < NOW()
                  AND status != 'DONE'
                ORDER BY due_date ASC
            """

            async with db_pool.get_db_connection() as conn:
                results = await conn.fetch(query, user_id)

            tasks = [_row_to_task(r) for r in results]

            return tasks

        except Exception as e:
            self.logger.error(f"Error retrieving overdue tasks for user {user_id}: {e}")
            raise