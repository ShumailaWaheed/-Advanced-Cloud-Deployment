"""RecurringTask entity model for the todo chatbot application."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import uuid
from src.utils.helpers import is_valid_uuid, get_current_iso_timestamp
from src.utils.constants import RecurrenceType


@dataclass
class RecurrencePattern:
    """Recurrence pattern definition."""
    type: str = "DAILY"
    interval: int = 1
    daysOfWeek: Optional[List[int]] = None
    dayOfMonth: Optional[int] = None
    month: Optional[int] = None
    startTime: Optional[str] = None

    def validate(self):
        valid_types = [t.value for t in RecurrenceType]
        if self.type not in valid_types:
            raise ValueError(f"Recurrence type must be one of: {', '.join(valid_types)}")
        if self.interval < 1:
            raise ValueError("Interval must be a positive integer")
        if self.daysOfWeek:
            if not all(0 <= d <= 6 for d in self.daysOfWeek):
                raise ValueError("Days of week must be between 0 (Sunday) and 6 (Saturday)")
        if self.dayOfMonth is not None and not (1 <= self.dayOfMonth <= 31):
            raise ValueError("Day of month must be between 1 and 31")
        if self.month is not None and not (1 <= self.month <= 12):
            raise ValueError("Month must be between 1 and 12")

    def to_dict(self) -> Dict[str, Any]:
        d = {"type": self.type, "interval": self.interval}
        if self.daysOfWeek is not None:
            d["daysOfWeek"] = self.daysOfWeek
        if self.dayOfMonth is not None:
            d["dayOfMonth"] = self.dayOfMonth
        if self.month is not None:
            d["month"] = self.month
        if self.startTime is not None:
            d["startTime"] = self.startTime
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecurrencePattern':
        return cls(
            type=data.get("type", "DAILY"),
            interval=data.get("interval", 1),
            daysOfWeek=data.get("daysOfWeek"),
            dayOfMonth=data.get("dayOfMonth"),
            month=data.get("month"),
            startTime=data.get("startTime"),
        )


@dataclass
class RecurringTask:
    """RecurringTask entity: template for tasks that repeat on a schedule."""

    recurringTaskId: str = field(default_factory=lambda: str(uuid.uuid4()))
    userId: str = ""
    title: str = ""
    description: Optional[str] = None
    priority: str = "MEDIUM"
    pattern: Optional[RecurrencePattern] = None
    isActive: bool = True
    endDate: Optional[str] = None
    createdAt: str = field(default_factory=get_current_iso_timestamp)
    updatedAt: str = field(default_factory=get_current_iso_timestamp)

    def __post_init__(self):
        if not self.recurringTaskId or not is_valid_uuid(self.recurringTaskId):
            self.recurringTaskId = str(uuid.uuid4())

    def validate(self):
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Title is required")
        if len(self.title) > 200:
            raise ValueError("Title must not exceed 200 characters")
        if not self.userId or not is_valid_uuid(self.userId):
            raise ValueError("userId must be a valid UUID")
        if self.pattern:
            self.pattern.validate()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recurringTaskId": self.recurringTaskId,
            "userId": self.userId,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "pattern": self.pattern.to_dict() if self.pattern else None,
            "isActive": self.isActive,
            "endDate": self.endDate,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecurringTask':
        pattern_data = data.get("pattern")
        pattern = RecurrencePattern.from_dict(pattern_data) if pattern_data else None
        return cls(
            recurringTaskId=data.get("recurringTaskId", str(uuid.uuid4())),
            userId=data.get("userId", ""),
            title=data.get("title", ""),
            description=data.get("description"),
            priority=data.get("priority", "MEDIUM"),
            pattern=pattern,
            isActive=data.get("isActive", True),
            endDate=data.get("endDate"),
            createdAt=data.get("createdAt", get_current_iso_timestamp()),
            updatedAt=data.get("updatedAt", get_current_iso_timestamp()),
        )
