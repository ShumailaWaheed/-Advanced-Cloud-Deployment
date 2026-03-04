"""RecurringTaskService for managing recurring tasks in the todo chatbot application."""

import logging
from typing import List, Optional, Dict, Any
import json

from src.models.recurring_task import RecurringTask, RecurrencePattern
from src.utils.database import db_pool
from src.utils.helpers import is_valid_uuid, get_current_iso_timestamp

logger = logging.getLogger(__name__)


class RecurringTaskService:
    """Service class for recurring task CRUD operations."""

    async def create_recurring_task(self, recurring_task: RecurringTask) -> RecurringTask:
        """Create a new recurring task template."""
        recurring_task.validate()
        now = get_current_iso_timestamp()
        recurring_task.createdAt = now
        recurring_task.updatedAt = now

        pattern_json = json.dumps(recurring_task.pattern.to_dict()) if recurring_task.pattern else None

        query = """
            INSERT INTO recurring_tasks (recurring_task_id, user_id, title, description, priority, pattern, is_active, end_date, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7, $8, $9, $10)
            RETURNING recurring_task_id, user_id, title, description, priority, pattern, is_active, end_date, created_at, updated_at
        """

        async with db_pool.get_db_connection() as conn:
            result = await conn.fetchrow(
                query,
                recurring_task.recurringTaskId,
                recurring_task.userId,
                recurring_task.title,
                recurring_task.description,
                recurring_task.priority,
                pattern_json,
                recurring_task.isActive,
                recurring_task.endDate,
                recurring_task.createdAt,
                recurring_task.updatedAt,
            )

        return self._row_to_model(result)

    async def get_recurring_tasks_by_user(self, user_id: str) -> List[RecurringTask]:
        """Get all recurring tasks for a user."""
        if not is_valid_uuid(user_id):
            raise ValueError("Invalid user ID format")

        query = """
            SELECT recurring_task_id, user_id, title, description, priority, pattern, is_active, end_date, created_at, updated_at
            FROM recurring_tasks WHERE user_id = $1 ORDER BY created_at DESC
        """
        async with db_pool.get_db_connection() as conn:
            results = await conn.fetch(query, user_id)
        return [self._row_to_model(r) for r in results]

    async def get_recurring_task_by_id(self, task_id: str, user_id: str) -> Optional[RecurringTask]:
        """Get a recurring task by ID."""
        query = """
            SELECT recurring_task_id, user_id, title, description, priority, pattern, is_active, end_date, created_at, updated_at
            FROM recurring_tasks WHERE recurring_task_id = $1 AND user_id = $2
        """
        async with db_pool.get_db_connection() as conn:
            result = await conn.fetchrow(query, task_id, user_id)
        return self._row_to_model(result) if result else None

    async def update_recurring_task(self, task_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[RecurringTask]:
        """Update a recurring task."""
        current = await self.get_recurring_task_by_id(task_id, user_id)
        if not current:
            return None

        title = update_data.get("title", current.title)
        description = update_data.get("description", current.description)
        priority = update_data.get("priority", current.priority)
        is_active = update_data.get("isActive", current.isActive)
        end_date = update_data.get("endDate", current.endDate)
        pattern = update_data.get("pattern")
        pattern_json = json.dumps(pattern) if pattern else (json.dumps(current.pattern.to_dict()) if current.pattern else None)
        now = get_current_iso_timestamp()

        query = """
            UPDATE recurring_tasks
            SET title = $1, description = $2, priority = $3, pattern = $4::jsonb, is_active = $5, end_date = $6, updated_at = $7
            WHERE recurring_task_id = $8 AND user_id = $9
            RETURNING recurring_task_id, user_id, title, description, priority, pattern, is_active, end_date, created_at, updated_at
        """
        async with db_pool.get_db_connection() as conn:
            result = await conn.fetchrow(query, title, description, priority, pattern_json, is_active, end_date, now, task_id, user_id)
        return self._row_to_model(result) if result else None

    async def delete_recurring_task(self, task_id: str, user_id: str) -> bool:
        """Delete a recurring task."""
        query = "DELETE FROM recurring_tasks WHERE recurring_task_id = $1 AND user_id = $2 RETURNING recurring_task_id"
        async with db_pool.get_db_connection() as conn:
            result = await conn.fetchrow(query, task_id, user_id)
        return result is not None

    async def get_active_recurring_tasks(self) -> List[RecurringTask]:
        """Get all active recurring tasks (for the recurrence engine)."""
        query = """
            SELECT recurring_task_id, user_id, title, description, priority, pattern, is_active, end_date, created_at, updated_at
            FROM recurring_tasks WHERE is_active = TRUE
        """
        async with db_pool.get_db_connection() as conn:
            results = await conn.fetch(query)
        return [self._row_to_model(r) for r in results]

    def _row_to_model(self, row) -> RecurringTask:
        """Convert a database row to a RecurringTask model."""
        pattern_data = row['pattern']
        if isinstance(pattern_data, str):
            pattern_data = json.loads(pattern_data)
        pattern = RecurrencePattern.from_dict(pattern_data) if pattern_data else None

        return RecurringTask(
            recurringTaskId=str(row['recurring_task_id']),
            userId=str(row['user_id']),
            title=row['title'],
            description=row['description'],
            priority=row['priority'],
            pattern=pattern,
            isActive=row['is_active'],
            endDate=row['end_date'].isoformat() + 'Z' if row['end_date'] else None,
            createdAt=row['created_at'].isoformat() + 'Z' if hasattr(row['created_at'], 'isoformat') else row['created_at'],
            updatedAt=row['updated_at'].isoformat() + 'Z' if hasattr(row['updated_at'], 'isoformat') else row['updated_at'],
        )
