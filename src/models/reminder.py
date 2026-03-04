"""Reminder entity model for the todo chatbot application."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import uuid
from src.utils.helpers import is_valid_uuid, get_current_iso_timestamp
from src.utils.constants import ReminderStatus, ReminderMethod


@dataclass
class Reminder:
    """Reminder entity: scheduled notification for task deadlines."""

    reminderId: str = field(default_factory=lambda: str(uuid.uuid4()))
    taskId: str = ""
    userId: str = ""
    scheduledTime: str = ""
    status: str = "SCHEDULED"
    method: str = "CHAT"
    createdAt: str = field(default_factory=get_current_iso_timestamp)
    sentAt: Optional[str] = None
    failureReason: Optional[str] = None

    def __post_init__(self):
        if not self.reminderId or not is_valid_uuid(self.reminderId):
            self.reminderId = str(uuid.uuid4())

    def validate(self):
        if not self.taskId or not is_valid_uuid(self.taskId):
            raise ValueError("taskId must be a valid UUID")
        if not self.userId or not is_valid_uuid(self.userId):
            raise ValueError("userId must be a valid UUID")
        if not self.scheduledTime:
            raise ValueError("scheduledTime is required")
        valid_statuses = [s.value for s in ReminderStatus]
        if self.status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        valid_methods = [m.value for m in ReminderMethod]
        if self.method not in valid_methods:
            raise ValueError(f"Method must be one of: {', '.join(valid_methods)}")

    def mark_sent(self):
        self.status = ReminderStatus.SENT.value
        self.sentAt = get_current_iso_timestamp()

    def mark_failed(self, reason: str):
        self.status = ReminderStatus.FAILED.value
        self.failureReason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reminderId": self.reminderId,
            "taskId": self.taskId,
            "userId": self.userId,
            "scheduledTime": self.scheduledTime,
            "status": self.status,
            "method": self.method,
            "createdAt": self.createdAt,
            "sentAt": self.sentAt,
            "failureReason": self.failureReason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reminder':
        return cls(
            reminderId=data.get("reminderId", str(uuid.uuid4())),
            taskId=data.get("taskId", ""),
            userId=data.get("userId", ""),
            scheduledTime=data.get("scheduledTime", ""),
            status=data.get("status", "SCHEDULED"),
            method=data.get("method", "CHAT"),
            createdAt=data.get("createdAt", get_current_iso_timestamp()),
            sentAt=data.get("sentAt"),
            failureReason=data.get("failureReason"),
        )
