"""ReminderService for scheduling reminders in the todo chatbot application."""

import logging
import os
from typing import List, Optional, Dict, Any

from src.models.reminder import Reminder
from src.utils.database import db_pool
from src.utils.helpers import is_valid_uuid, get_current_iso_timestamp
from src.utils.constants import ReminderStatus, DAPR_PUBSUB_NAME, REMINDERS_TOPIC

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


class ReminderService:
    """Service class for scheduling and managing reminders via Dapr Jobs API."""

    DAPR_PORT = os.getenv("DAPR_HTTP_PORT", "3500")

    def __init__(self):
        self.dapr_url = f"http://localhost:{self.DAPR_PORT}"

    async def schedule_reminder(self, reminder: Reminder) -> Reminder:
        """Schedule a new reminder."""
        reminder.validate()
        reminder.createdAt = get_current_iso_timestamp()

        query = """
            INSERT INTO reminders (reminder_id, task_id, user_id, scheduled_time, status, method, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING reminder_id, task_id, user_id, scheduled_time, status, method, created_at, sent_at, failure_reason
        """
        async with db_pool.get_db_connection() as conn:
            result = await conn.fetchrow(
                query,
                reminder.reminderId,
                reminder.taskId,
                reminder.userId,
                reminder.scheduledTime,
                reminder.status,
                reminder.method,
                reminder.createdAt,
            )

        created = self._row_to_model(result)

        # Schedule via Dapr Jobs API
        await self._schedule_dapr_job(created)

        # Publish reminder.scheduled event
        await self._publish_event("reminder.scheduled", created.to_dict())

        logger.info(f"Reminder scheduled: {created.reminderId}")
        return created

    async def get_reminders_by_user(self, user_id: str) -> List[Reminder]:
        """Get all reminders for a user."""
        if not is_valid_uuid(user_id):
            raise ValueError("Invalid user ID format")

        query = """
            SELECT reminder_id, task_id, user_id, scheduled_time, status, method, created_at, sent_at, failure_reason
            FROM reminders WHERE user_id = $1 ORDER BY scheduled_time ASC
        """
        async with db_pool.get_db_connection() as conn:
            results = await conn.fetch(query, user_id)
        return [self._row_to_model(r) for r in results]

    async def get_reminders_by_task(self, task_id: str) -> List[Reminder]:
        """Get reminders for a specific task."""
        query = """
            SELECT reminder_id, task_id, user_id, scheduled_time, status, method, created_at, sent_at, failure_reason
            FROM reminders WHERE task_id = $1 ORDER BY scheduled_time ASC
        """
        async with db_pool.get_db_connection() as conn:
            results = await conn.fetch(query, task_id)
        return [self._row_to_model(r) for r in results]

    async def mark_sent(self, reminder_id: str) -> Optional[Reminder]:
        """Mark a reminder as sent."""
        now = get_current_iso_timestamp()
        query = """
            UPDATE reminders SET status = $1, sent_at = $2 WHERE reminder_id = $3
            RETURNING reminder_id, task_id, user_id, scheduled_time, status, method, created_at, sent_at, failure_reason
        """
        async with db_pool.get_db_connection() as conn:
            result = await conn.fetchrow(query, ReminderStatus.SENT.value, now, reminder_id)
        if result:
            reminder = self._row_to_model(result)
            await self._publish_event("reminder.sent", reminder.to_dict())
            return reminder
        return None

    async def mark_failed(self, reminder_id: str, reason: str) -> Optional[Reminder]:
        """Mark a reminder as failed."""
        query = """
            UPDATE reminders SET status = $1, failure_reason = $2 WHERE reminder_id = $3
            RETURNING reminder_id, task_id, user_id, scheduled_time, status, method, created_at, sent_at, failure_reason
        """
        async with db_pool.get_db_connection() as conn:
            result = await conn.fetchrow(query, ReminderStatus.FAILED.value, reason, reminder_id)
        if result:
            reminder = self._row_to_model(result)
            await self._publish_event("reminder.failed", reminder.to_dict())
            return reminder
        return None

    async def cancel_reminders_for_task(self, task_id: str) -> int:
        """Cancel all pending reminders for a task."""
        query = """
            DELETE FROM reminders WHERE task_id = $1 AND status = $2 RETURNING reminder_id
        """
        async with db_pool.get_db_connection() as conn:
            results = await conn.fetch(query, task_id, ReminderStatus.SCHEDULED.value)
        return len(results)

    async def _schedule_dapr_job(self, reminder: Reminder) -> bool:
        """Schedule a reminder via Dapr Jobs API."""
        if httpx is None:
            logger.warning("httpx not available; skipping Dapr job scheduling")
            return False

        url = f"{self.dapr_url}/v1.0-alpha1/jobs/{reminder.reminderId}"
        job_data = {
            "schedule": f"@every 0s",  # One-time trigger
            "dueTime": reminder.scheduledTime,
            "data": reminder.to_dict(),
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.put(url, json=job_data)
                return response.status_code in (200, 204)
        except Exception as e:
            logger.error(f"Failed to schedule Dapr job: {e}")
            return False

    async def _publish_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Publish a reminder event to Dapr pub/sub."""
        if httpx is None:
            return False

        url = f"{self.dapr_url}/v1.0/publish/{DAPR_PUBSUB_NAME}/{REMINDERS_TOPIC}"
        event_data = {
            "eventType": event_type,
            "timestamp": get_current_iso_timestamp(),
            "data": data,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=event_data)
                return response.status_code in (200, 204)
        except Exception as e:
            logger.error(f"Failed to publish reminder event: {e}")
            return False

    def _row_to_model(self, row) -> Reminder:
        return Reminder(
            reminderId=str(row['reminder_id']),
            taskId=str(row['task_id']),
            userId=str(row['user_id']),
            scheduledTime=row['scheduled_time'].isoformat() + 'Z' if hasattr(row['scheduled_time'], 'isoformat') else row['scheduled_time'],
            status=row['status'],
            method=row['method'],
            createdAt=row['created_at'].isoformat() + 'Z' if hasattr(row['created_at'], 'isoformat') else row['created_at'],
            sentAt=row['sent_at'].isoformat() + 'Z' if row['sent_at'] and hasattr(row['sent_at'], 'isoformat') else row.get('sent_at'),
            failureReason=row['failure_reason'],
        )
