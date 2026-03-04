"""Task entity model for the todo chatbot application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid
from src.utils.constants import TaskPriority, TaskStatus
from src.utils.helpers import is_valid_uuid, get_current_iso_timestamp


@dataclass
class Task:
    """Task entity representing a single task with properties and state."""

    # Core fields
    taskId: str = field(default_factory=lambda: str(uuid.uuid4()))
    userId: str = ""
    title: str = ""

    # Optional fields
    description: Optional[str] = None
    dueDate: Optional[str] = None  # ISO 8601 format string
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TO_DO
    tags: List[str] = field(default_factory=list)
    createdAt: str = field(default_factory=get_current_iso_timestamp)
    updatedAt: str = field(default_factory=get_current_iso_timestamp)
    completedAt: Optional[str] = None
    recurrencePattern: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate the task after initialization."""
        self.validate()

        # Ensure taskId is a valid UUID string
        if not self.taskId or not is_valid_uuid(self.taskId):
            self.taskId = str(uuid.uuid4())

        # Ensure userId is a valid UUID string
        if not self.userId or not is_valid_uuid(self.userId):
            raise ValueError("userId must be a valid UUID")

    def validate(self):
        """Validate the task data."""
        # Validate title
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Title is required")

        if len(self.title) > 200:
            raise ValueError("Title must be 200 characters or less")

        # Validate user ID
        if not self.userId:
            raise ValueError("User ID is required")

        if not is_valid_uuid(self.userId):
            raise ValueError("User ID must be a valid UUID")

        # Validate priority
        if isinstance(self.priority, str):
            try:
                self.priority = TaskPriority(self.priority.upper())
            except ValueError:
                raise ValueError(f"Invalid priority: {self.priority}. Must be one of {list(TaskPriority)}")

        # Validate status
        if isinstance(self.status, str):
            try:
                self.status = TaskStatus(self.status.upper())
            except ValueError:
                raise ValueError(f"Invalid status: {self.status}. Must be one of {list(TaskStatus)}")

        # Validate tags
        if self.tags:
            if len(self.tags) > 5:
                raise ValueError("A task cannot have more than 5 tags")

            for tag in self.tags:
                if len(tag) > 50:
                    raise ValueError(f"Tag '{tag}' exceeds 50 characters")

                if len(tag.strip()) == 0:
                    raise ValueError("Tags cannot be empty")

        # Validate due date if provided
        if self.dueDate:
            # Basic ISO format validation (could be enhanced)
            if not isinstance(self.dueDate, str) or len(self.dueDate) < 10:
                raise ValueError("Due date must be a valid ISO 8601 format string")

        # Validate recurrence pattern if provided
        if self.recurrencePattern:
            if not isinstance(self.recurrencePattern, dict):
                raise ValueError("Recurrence pattern must be a dictionary")

    def update_title(self, new_title: str):
        """Update the task title."""
        if not new_title or len(new_title.strip()) == 0:
            raise ValueError("Title cannot be empty")

        if len(new_title) > 200:
            raise ValueError("Title must be 200 characters or less")

        self.title = new_title
        self.updatedAt = get_current_iso_timestamp()

    def update_description(self, new_description: Optional[str]):
        """Update the task description."""
        if new_description and len(new_description) > 2000:
            raise ValueError("Description must be 2000 characters or less")

        self.description = new_description
        self.updatedAt = get_current_iso_timestamp()

    def update_due_date(self, new_due_date: Optional[str]):
        """Update the task due date."""
        if new_due_date:
            # Basic validation
            if not isinstance(new_due_date, str) or len(new_due_date) < 10:
                raise ValueError("Due date must be a valid ISO 8601 format string")

        self.dueDate = new_due_date
        self.updatedAt = get_current_iso_timestamp()

    def update_priority(self, new_priority: TaskPriority):
        """Update the task priority."""
        if isinstance(new_priority, str):
            new_priority = TaskPriority(new_priority.upper())

        self.priority = new_priority
        self.updatedAt = get_current_iso_timestamp()

    def update_status(self, new_status: TaskStatus):
        """Update the task status."""
        if isinstance(new_status, str):
            new_status = TaskStatus(new_status.upper())

        old_status = self.status
        self.status = new_status
        self.updatedAt = get_current_iso_timestamp()

        # Update completedAt if status changed to DONE
        if new_status == TaskStatus.DONE and old_status != TaskStatus.DONE:
            self.completedAt = get_current_iso_timestamp()
        elif new_status != TaskStatus.DONE:
            self.completedAt = None

    def add_tag(self, tag: str):
        """Add a tag to the task."""
        if not tag or len(tag.strip()) == 0:
            raise ValueError("Tag cannot be empty")

        if len(tag) > 50:
            raise ValueError(f"Tag '{tag}' exceeds 50 characters")

        if len(self.tags) >= 5:
            raise ValueError("A task cannot have more than 5 tags")

        if tag not in self.tags:
            self.tags.append(tag)
            self.updatedAt = get_current_iso_timestamp()

    def remove_tag(self, tag: str):
        """Remove a tag from the task."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updatedAt = get_current_iso_timestamp()

    def update_recurrence_pattern(self, pattern: Optional[Dict[str, Any]]):
        """Update the recurrence pattern."""
        if pattern:
            if not isinstance(pattern, dict):
                raise ValueError("Recurrence pattern must be a dictionary")

        self.recurrencePattern = pattern
        self.updatedAt = get_current_iso_timestamp()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary."""
        return {
            "taskId": self.taskId,
            "userId": self.userId,
            "title": self.title,
            "description": self.description,
            "dueDate": self.dueDate,
            "priority": self.priority.value if hasattr(self.priority, 'value') else self.priority,
            "status": self.status.value if hasattr(self.status, 'value') else self.status,
            "tags": self.tags,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
            "completedAt": self.completedAt,
            "recurrencePattern": self.recurrencePattern
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create a Task instance from a dictionary."""
        # Handle string priority/status conversion
        priority = data.get('priority', TaskPriority.MEDIUM)
        if isinstance(priority, str):
            priority = TaskPriority(priority.upper())

        status = data.get('status', TaskStatus.TO_DO)
        if isinstance(status, str):
            status = TaskStatus(status.upper())

        return cls(
            taskId=data.get('taskId', ''),
            userId=data.get('userId', ''),
            title=data.get('title', ''),
            description=data.get('description'),
            dueDate=data.get('dueDate'),
            priority=priority,
            status=status,
            tags=data.get('tags', []),
            createdAt=data.get('createdAt', get_current_iso_timestamp()),
            updatedAt=data.get('updatedAt', get_current_iso_timestamp()),
            completedAt=data.get('completedAt'),
            recurrencePattern=data.get('recurrencePattern')
        )