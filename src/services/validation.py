"""Task validation logic for the todo chatbot application."""

from typing import Optional, List, Dict, Any
from datetime import datetime

from src.utils.constants import (
    TaskPriority, TaskStatus,
    MAX_TITLE_LENGTH, MAX_DESCRIPTION_LENGTH,
    MAX_TAGS_PER_TASK, MAX_TAG_LENGTH,
)


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class TaskValidator:
    """Comprehensive validation for task data."""

    @staticmethod
    def validate_title(title: Optional[str]) -> str:
        """Validate task title."""
        if not title or len(title.strip()) == 0:
            raise ValidationError("title", "Title is required")
        title = title.strip()
        if len(title) > MAX_TITLE_LENGTH:
            raise ValidationError("title", f"Title must not exceed {MAX_TITLE_LENGTH} characters")
        return title

    @staticmethod
    def validate_description(description: Optional[str]) -> Optional[str]:
        """Validate task description."""
        if description is None:
            return None
        description = description.strip()
        if len(description) > MAX_DESCRIPTION_LENGTH:
            raise ValidationError("description", f"Description must not exceed {MAX_DESCRIPTION_LENGTH} characters")
        return description

    @staticmethod
    def validate_due_date(due_date: Optional[str]) -> Optional[str]:
        """Validate task due date."""
        if due_date is None:
            return None

        try:
            if isinstance(due_date, str):
                parsed = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            else:
                parsed = due_date
            return due_date
        except (ValueError, TypeError):
            raise ValidationError("dueDate", "Due date must be a valid ISO 8601 datetime")

    @staticmethod
    def validate_priority(priority: Optional[str]) -> str:
        """Validate task priority."""
        if priority is None:
            return TaskPriority.MEDIUM.value

        priority_upper = priority.upper() if isinstance(priority, str) else priority
        valid_priorities = [p.value for p in TaskPriority]
        if priority_upper not in valid_priorities:
            raise ValidationError("priority", f"Priority must be one of: {', '.join(valid_priorities)}")
        return priority_upper

    @staticmethod
    def validate_status(status: Optional[str]) -> str:
        """Validate task status."""
        if status is None:
            return TaskStatus.TO_DO.value

        status_upper = status.upper() if isinstance(status, str) else status
        valid_statuses = [s.value for s in TaskStatus]
        if status_upper not in valid_statuses:
            raise ValidationError("status", f"Status must be one of: {', '.join(valid_statuses)}")
        return status_upper

    @staticmethod
    def validate_tags(tags: Optional[List[str]]) -> List[str]:
        """Validate task tags."""
        if tags is None:
            return []

        if not isinstance(tags, list):
            raise ValidationError("tags", "Tags must be a list")

        if len(tags) > MAX_TAGS_PER_TASK:
            raise ValidationError("tags", f"Maximum {MAX_TAGS_PER_TASK} tags allowed")

        validated_tags = []
        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                raise ValidationError("tags", f"Tag at index {i} must be a string")

            tag = tag.strip()
            if len(tag) == 0:
                continue
            if len(tag) > MAX_TAG_LENGTH:
                raise ValidationError("tags", f"Each tag must not exceed {MAX_TAG_LENGTH} characters")
            if not all(c.isalnum() or c in ' -' for c in tag):
                raise ValidationError("tags", "Tags can only contain alphanumeric characters, spaces, and hyphens")
            validated_tags.append(tag)

        return validated_tags

    @classmethod
    def validate_create_task(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all fields for task creation."""
        return {
            "title": cls.validate_title(data.get("title")),
            "description": cls.validate_description(data.get("description")),
            "dueDate": cls.validate_due_date(data.get("dueDate")),
            "priority": cls.validate_priority(data.get("priority")),
            "status": cls.validate_status(data.get("status")),
            "tags": cls.validate_tags(data.get("tags")),
        }

    @classmethod
    def validate_update_task(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate fields for task update (all optional)."""
        validated = {}
        if "title" in data:
            validated["title"] = cls.validate_title(data["title"])
        if "description" in data:
            validated["description"] = cls.validate_description(data["description"])
        if "dueDate" in data:
            validated["dueDate"] = cls.validate_due_date(data["dueDate"])
        if "priority" in data:
            validated["priority"] = cls.validate_priority(data["priority"])
        if "status" in data:
            validated["status"] = cls.validate_status(data["status"])
        if "tags" in data:
            validated["tags"] = cls.validate_tags(data["tags"])
        return validated
