"""TaskEvent entity model for the todo chatbot application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, Union
from uuid import UUID
import uuid
from src.utils.constants import EventType
from src.utils.helpers import is_valid_uuid, get_current_iso_timestamp


@dataclass
class TaskEvent:
    """TaskEvent entity representing changes to tasks in the system."""

    # Core fields
    eventId: str = field(default_factory=lambda: str(uuid.uuid4()))
    eventType: EventType = EventType.TASK_CREATED
    taskId: str = ""
    userId: str = ""
    timestamp: str = field(default_factory=get_current_iso_timestamp)
    newData: Dict[str, Any] = field(default_factory=dict)

    # Optional fields
    previousData: Optional[Dict[str, Any]] = None
    correlationId: Optional[str] = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Validate the task event after initialization."""
        self.validate()

        # Ensure eventId is a valid UUID string
        if not self.eventId or not is_valid_uuid(self.eventId):
            self.eventId = str(uuid.uuid4())

        # Ensure correlationId is a valid UUID string
        if not self.correlationId or not is_valid_uuid(self.correlationId):
            self.correlationId = str(uuid.uuid4())

    def validate(self):
        """Validate the task event data."""
        # Validate event type
        if isinstance(self.eventType, str):
            try:
                self.eventType = EventType(self.eventType.lower().replace('.', '_'))
            except ValueError:
                raise ValueError(f"Invalid event type: {self.eventType}")

        # Validate task ID
        if not self.taskId or not is_valid_uuid(self.taskId):
            raise ValueError("taskId must be a valid UUID")

        # Validate user ID
        if not self.userId or not is_valid_uuid(self.userId):
            raise ValueError("userId must be a valid UUID")

        # Validate timestamp
        if not self.timestamp:
            raise ValueError("Timestamp is required")

        # Validate newData
        if not self.newData or not isinstance(self.newData, dict):
            raise ValueError("newData is required and must be a dictionary")

        # Validate previousData if provided
        if self.previousData is not None and not isinstance(self.previousData, dict):
            raise ValueError("previousData must be a dictionary or None")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task event to a dictionary."""
        return {
            "eventId": self.eventId,
            "eventType": self.eventType.value if hasattr(self.eventType, 'value') else self.eventType,
            "taskId": self.taskId,
            "userId": self.userId,
            "timestamp": self.timestamp,
            "previousData": self.previousData,
            "newData": self.newData,
            "correlationId": self.correlationId
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskEvent':
        """Create a TaskEvent instance from a dictionary."""
        # Handle string event type conversion
        event_type = data.get('eventType', EventType.TASK_CREATED)
        if isinstance(event_type, str):
            # Convert string to enum
            try:
                event_type = EventType(event_type.lower().replace('.', '_'))
            except ValueError:
                # If the exact value doesn't exist, try to match closest
                for evt in EventType:
                    if event_type.lower() == evt.value.lower():
                        event_type = evt
                        break
                else:
                    # Default to TASK_CREATED if no match
                    event_type = EventType.TASK_CREATED

        return cls(
            eventId=data.get('eventId', str(uuid.uuid4())),
            eventType=event_type,
            taskId=data.get('taskId', ''),
            userId=data.get('userId', ''),
            timestamp=data.get('timestamp', get_current_iso_timestamp()),
            newData=data.get('newData', {}),
            previousData=data.get('previousData'),
            correlationId=data.get('correlationId', str(uuid.uuid4()))
        )


@dataclass
class EventMetadata:
    """Metadata for events in the system."""

    eventId: str = field(default_factory=lambda: str(uuid.uuid4()))
    eventType: str = ""
    timestamp: str = field(default_factory=get_current_iso_timestamp)
    userId: str = ""
    taskId: Optional[str] = None
    correlationId: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = ""
    version: str = "1.0"

    def validate(self):
        """Validate the event metadata."""
        if not self.eventType:
            raise ValueError("Event type is required")

        if not self.userId or not is_valid_uuid(self.userId):
            raise ValueError("userId must be a valid UUID")

        if self.taskId and not is_valid_uuid(self.taskId):
            raise ValueError("taskId must be a valid UUID if provided")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the event metadata to a dictionary."""
        return {
            "eventId": self.eventId,
            "eventType": self.eventType,
            "timestamp": self.timestamp,
            "userId": self.userId,
            "taskId": self.taskId,
            "correlationId": self.correlationId,
            "source": self.source,
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventMetadata':
        """Create an EventMetadata instance from a dictionary."""
        return cls(
            eventId=data.get('eventId', str(uuid.uuid4())),
            eventType=data.get('eventType', ''),
            timestamp=data.get('timestamp', get_current_iso_timestamp()),
            userId=data.get('userId', ''),
            taskId=data.get('taskId'),
            correlationId=data.get('correlationId', str(uuid.uuid4())),
            source=data.get('source', ''),
            version=data.get('version', '1.0')
        )