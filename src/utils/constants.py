"""Constants for the todo chatbot application."""

from enum import Enum


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TaskStatus(Enum):
    """Task status values."""
    TO_DO = "TO_DO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class ReminderMethod(Enum):
    """Reminder delivery methods."""
    CHAT = "CHAT"
    EMAIL = "EMAIL"
    PUSH = "PUSH"


class ReminderStatus(Enum):
    """Reminder status values."""
    SCHEDULED = "SCHEDULED"
    SENT = "SENT"
    FAILED = "FAILED"


class RecurrenceType(Enum):
    """Types of recurrence patterns."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class EventType(Enum):
    """Types of events in the system."""
    # Task events
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    TASK_COMPLETED = "task.completed"
    TASK_PRIORITY_CHANGED = "task.priority.changed"
    TASK_DUE_DATE_CHANGED = "task.due.date.changed"
    TASK_TAGS_CHANGED = "task.tags.changed"

    # Recurring task events
    RECURRING_TASK_CREATED = "recurring-task.created"
    RECURRING_TASK_TRIGGERED = "recurring-task.triggered"
    RECURRING_TASK_UPDATED = "recurring-task.updated"

    # User events
    USER_PROFILE_UPDATED = "user.profile.updated"
    USER_CREATED = "user.created"

    # Reminder events
    REMINDER_SCHEDULED = "reminder.scheduled"
    REMINDER_SENT = "reminder.sent"
    REMINDER_FAILED = "reminder.failed"
    REMINDER_RESCHEDULED = "reminder.rescheduled"


# Validation constants
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 2000
MAX_TAGS_PER_TASK = 5
MAX_TAG_LENGTH = 50
MAX_USERNAME_LENGTH = 50
USERNAME_MIN_LENGTH = 3

# Database constants
POSTGRES_SCHEMA_NAME = "todochatbot"

# Dapr constants
DAPR_STATE_STORE_NAME = "statestore"
DAPR_PUBSUB_NAME = "pubsub"
DAPR_SECRET_STORE_NAME = "secrets-store"

# Kafka topic names
TASK_EVENTS_TOPIC = "task-events"
REMINDERS_TOPIC = "reminders"
USER_EVENTS_TOPIC = "user-events"

# API constants
API_VERSION = "v1"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Timeout constants (in seconds)
HTTP_TIMEOUT = 30
DATABASE_TIMEOUT = 10
CACHE_TIMEOUT = 300