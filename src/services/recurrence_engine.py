"""RecurrenceEngine for generating task instances from recurring task templates."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from src.models.recurring_task import RecurringTask
from src.models.task import Task
from src.services.task_service import TaskService
from src.services.task_event_service import TaskEventService
from src.utils.constants import TaskPriority, TaskStatus, EventType
from src.utils.helpers import get_current_iso_timestamp

logger = logging.getLogger(__name__)

task_service = TaskService()
event_service = TaskEventService()


class RecurrenceEngine:
    """Engine for generating task instances from recurring task templates."""

    @staticmethod
    def calculate_next_occurrence(recurring_task: RecurringTask, from_date: Optional[datetime] = None) -> Optional[datetime]:
        """Calculate the next occurrence based on the recurrence pattern."""
        if not recurring_task.pattern:
            return None

        now = from_date or datetime.utcnow()
        pattern = recurring_task.pattern

        if pattern.type == "DAILY":
            return now + timedelta(days=pattern.interval)
        elif pattern.type == "WEEKLY":
            if pattern.daysOfWeek:
                # Find the next matching day of week
                for delta in range(1, 8):
                    candidate = now + timedelta(days=delta)
                    if candidate.weekday() in [
                        (d - 1) % 7 for d in pattern.daysOfWeek  # Convert Sun=0 to Mon=0
                    ]:
                        return candidate
            return now + timedelta(weeks=pattern.interval)
        elif pattern.type == "MONTHLY":
            month = now.month + pattern.interval
            year = now.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            day = min(pattern.dayOfMonth or now.day, 28)  # Safe day
            return datetime(year, month, day, now.hour, now.minute)
        elif pattern.type == "YEARLY":
            return datetime(now.year + pattern.interval, pattern.month or now.month, now.day, now.hour, now.minute)

        return None

    @staticmethod
    async def generate_task_instance(recurring_task: RecurringTask, due_date: datetime) -> Task:
        """Generate a new task instance from a recurring task template."""
        task = Task(
            taskId=str(uuid.uuid4()),
            userId=recurring_task.userId,
            title=recurring_task.title,
            description=recurring_task.description,
            dueDate=due_date.isoformat() + 'Z',
            priority=TaskPriority(recurring_task.priority),
            status=TaskStatus.TO_DO,
            tags=[],
            recurrencePattern=recurring_task.pattern.to_dict() if recurring_task.pattern else None,
        )

        created = await task_service.create_task(task)

        # Publish events
        await event_service.publish_task_created(created)
        await event_service.publish_event(
            EventType.RECURRING_TASK_TRIGGERED,
            created,
            previous_data={"recurringTaskId": recurring_task.recurringTaskId},
        )

        logger.info(f"Generated task instance {created.taskId} from recurring task {recurring_task.recurringTaskId}")
        return created

    @staticmethod
    async def process_recurring_tasks(recurring_tasks: List[RecurringTask]) -> List[Task]:
        """Process a list of recurring tasks and generate instances where needed."""
        generated = []
        for rt in recurring_tasks:
            if not rt.isActive:
                continue

            # Check end date
            if rt.endDate:
                try:
                    end = datetime.fromisoformat(rt.endDate.replace('Z', '+00:00'))
                    if datetime.utcnow() > end.replace(tzinfo=None):
                        continue
                except (ValueError, TypeError):
                    pass

            next_date = RecurrenceEngine.calculate_next_occurrence(rt)
            if next_date:
                task = await RecurrenceEngine.generate_task_instance(rt, next_date)
                generated.append(task)

        return generated
