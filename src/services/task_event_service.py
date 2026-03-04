"""TaskEventService for event publishing in the todo chatbot application."""

import logging
import os
from typing import Optional, Dict, Any, List
import uuid

from src.models.task_event import TaskEvent, EventMetadata
from src.models.task import Task
from src.utils.database import db_pool
from src.utils.constants import (
    EventType, DAPR_PUBSUB_NAME, TASK_EVENTS_TOPIC,
    USER_EVENTS_TOPIC, REMINDERS_TOPIC,
)
from src.utils.helpers import get_current_iso_timestamp, is_valid_uuid

try:
    import httpx
except ImportError:
    httpx = None


class TaskEventService:
    """Service class for publishing and persisting task events via Dapr pub/sub."""

    DAPR_PORT = os.getenv("DAPR_HTTP_PORT", "3500")

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dapr_url = f"http://localhost:{self.DAPR_PORT}/v1.0"

    async def _publish_to_dapr(self, topic: str, event_data: Dict[str, Any]) -> bool:
        """Publish an event to Dapr pub/sub."""
        if httpx is None:
            self.logger.warning("httpx not available; skipping Dapr publish")
            return False

        url = f"{self.dapr_url}/publish/{DAPR_PUBSUB_NAME}/{topic}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=event_data)
                if response.status_code in (200, 204):
                    self.logger.info(f"Event published to {topic}: {event_data.get('eventType')}")
                    return True
                self.logger.error(f"Failed to publish event: {response.status_code} {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error publishing event to Dapr: {e}")
            return False

    async def _persist_event(self, event: TaskEvent) -> None:
        """Persist an event to the task_events table."""
        query = """
            INSERT INTO task_events (event_id, event_type, task_id, user_id, timestamp, previous_data, new_data, correlation_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """
        event_type_value = event.eventType.value if hasattr(event.eventType, 'value') else str(event.eventType)
        try:
            async with db_pool.get_db_connection() as conn:
                await conn.execute(
                    query,
                    event.eventId,
                    event_type_value,
                    event.taskId,
                    event.userId,
                    event.timestamp,
                    event.previousData,
                    event.newData,
                    event.correlationId,
                )
            self.logger.info(f"Event persisted: {event.eventId}")
        except Exception as e:
            self.logger.error(f"Error persisting event: {e}")

    async def publish_event(
        self,
        event_type: EventType,
        task: Task,
        previous_data: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> TaskEvent:
        """Create, persist, and publish a task event."""
        event = TaskEvent(
            eventId=str(uuid.uuid4()),
            eventType=event_type,
            taskId=task.taskId,
            userId=task.userId,
            timestamp=get_current_iso_timestamp(),
            newData=task.to_dict(),
            previousData=previous_data,
            correlationId=correlation_id or str(uuid.uuid4()),
        )

        # Persist to database
        await self._persist_event(event)

        # Publish to Dapr
        await self._publish_to_dapr(TASK_EVENTS_TOPIC, event.to_dict())

        return event

    async def publish_task_created(self, task: Task, correlation_id: Optional[str] = None) -> TaskEvent:
        """Publish a task.created event."""
        return await self.publish_event(EventType.TASK_CREATED, task, correlation_id=correlation_id)

    async def publish_task_updated(
        self, task: Task, previous_data: Dict[str, Any], correlation_id: Optional[str] = None
    ) -> TaskEvent:
        """Publish a task.updated event."""
        return await self.publish_event(EventType.TASK_UPDATED, task, previous_data, correlation_id)

    async def publish_task_deleted(self, task: Task, correlation_id: Optional[str] = None) -> TaskEvent:
        """Publish a task.deleted event."""
        return await self.publish_event(EventType.TASK_DELETED, task, correlation_id=correlation_id)

    async def publish_task_completed(
        self, task: Task, previous_data: Dict[str, Any], correlation_id: Optional[str] = None
    ) -> TaskEvent:
        """Publish a task.completed event."""
        return await self.publish_event(EventType.TASK_COMPLETED, task, previous_data, correlation_id)

    async def publish_task_priority_changed(
        self, task: Task, previous_data: Dict[str, Any], correlation_id: Optional[str] = None
    ) -> TaskEvent:
        """Publish a task.priority.changed event."""
        return await self.publish_event(EventType.TASK_PRIORITY_CHANGED, task, previous_data, correlation_id)

    async def publish_task_due_date_changed(
        self, task: Task, previous_data: Dict[str, Any], correlation_id: Optional[str] = None
    ) -> TaskEvent:
        """Publish a task.due.date.changed event."""
        return await self.publish_event(EventType.TASK_DUE_DATE_CHANGED, task, previous_data, correlation_id)

    async def publish_user_event(self, event_type: EventType, user_data: Dict[str, Any]) -> bool:
        """Publish a user event to the user-events topic."""
        event_data = {
            "eventType": event_type.value,
            "userId": user_data.get("userId", ""),
            "timestamp": get_current_iso_timestamp(),
            "correlationId": str(uuid.uuid4()),
            "data": user_data,
        }
        return await self._publish_to_dapr(USER_EVENTS_TOPIC, event_data)

    async def get_events_by_task(self, task_id: str, limit: int = 50) -> List[TaskEvent]:
        """Get all events for a specific task."""
        if not is_valid_uuid(task_id):
            raise ValueError("Invalid task ID format")

        query = """
            SELECT event_id, event_type, task_id, user_id, timestamp,
                   previous_data, new_data, correlation_id
            FROM task_events
            WHERE task_id = $1
            ORDER BY timestamp DESC
            LIMIT $2
        """
        async with db_pool.get_db_connection() as conn:
            results = await conn.fetch(query, task_id, limit)

        return [
            TaskEvent(
                eventId=str(r['event_id']),
                eventType=EventType(r['event_type']),
                taskId=str(r['task_id']),
                userId=str(r['user_id']),
                timestamp=r['timestamp'].isoformat() + 'Z' if hasattr(r['timestamp'], 'isoformat') else r['timestamp'],
                previousData=r['previous_data'],
                newData=r['new_data'],
                correlationId=str(r['correlation_id']) if r['correlation_id'] else None,
            )
            for r in results
        ]

    async def get_events_by_user(self, user_id: str, limit: int = 50) -> List[TaskEvent]:
        """Get all events for a specific user."""
        if not is_valid_uuid(user_id):
            raise ValueError("Invalid user ID format")

        query = """
            SELECT event_id, event_type, task_id, user_id, timestamp,
                   previous_data, new_data, correlation_id
            FROM task_events
            WHERE user_id = $1
            ORDER BY timestamp DESC
            LIMIT $2
        """
        async with db_pool.get_db_connection() as conn:
            results = await conn.fetch(query, user_id, limit)

        return [
            TaskEvent(
                eventId=str(r['event_id']),
                eventType=EventType(r['event_type']),
                taskId=str(r['task_id']),
                userId=str(r['user_id']),
                timestamp=r['timestamp'].isoformat() + 'Z' if hasattr(r['timestamp'], 'isoformat') else r['timestamp'],
                previousData=r['previous_data'],
                newData=r['new_data'],
                correlationId=str(r['correlation_id']) if r['correlation_id'] else None,
            )
            for r in results
        ]
