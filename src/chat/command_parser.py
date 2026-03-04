"""Chat command parser for the todo chatbot application."""

import re
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParsedCommand:
    """Represents a parsed chat command."""
    action: str  # create, update, delete, get, search, filter, sort, help, unknown
    entity: str  # task, recurring-task, reminder
    params: Dict[str, Any]
    raw_text: str


class CommandParser:
    """Parses natural language chat commands into structured actions."""

    # Command patterns (order matters - more specific first)
    PATTERNS = [
        # Create task
        (r"(?:create|add|new)\s+(?:a\s+)?(?:recurring\s+)?task[:\s]+(.+)",
         "create", "task"),
        # Delete task
        (r"(?:delete|remove|cancel)\s+task\s+#?(\S+)",
         "delete", "task"),
        # Complete task
        (r"(?:complete|finish|done)\s+task\s+#?(\S+)",
         "complete", "task"),
        # Update task
        (r"(?:update|edit|modify|change)\s+task\s+#?(\S+)\s+(.*)",
         "update", "task"),
        # Get specific task
        (r"(?:show|get|view|describe)\s+task\s+#?(\S+)",
         "get_one", "task"),
        # List / get tasks
        (r"(?:show|get|list|view)\s+(?:all\s+)?(?:my\s+)?tasks?",
         "get", "task"),
        # Search tasks
        (r"(?:search|find)\s+tasks?\s+(?:tagged?|with\s+tag)[:\s]+(\S+)",
         "search_tag", "task"),
        (r"(?:search|find)\s+tasks?\s+(.*)",
         "search", "task"),
        # Filter tasks
        (r"(?:show|filter|get)\s+(\w+)\s+priority\s+tasks?",
         "filter_priority", "task"),
        (r"(?:show|filter|get)\s+(\w+)\s+tasks?",
         "filter_status", "task"),
        # Sort tasks
        (r"(?:sort)\s+tasks?\s+by\s+(\w+)(?:\s+(asc|desc))?",
         "sort", "task"),
        # Recurring tasks
        (r"(?:create|add|new)\s+recurring\s+task[:\s]+(.*)",
         "create", "recurring-task"),
        # Schedule reminder
        (r"(?:schedule|set|create)\s+(?:a\s+)?reminder\s+(.*)",
         "create", "reminder"),
        # Help
        (r"(?:help|commands|what\s+can\s+you\s+do)",
         "help", "system"),
    ]

    @classmethod
    def parse(cls, message: str) -> ParsedCommand:
        """Parse a chat message into a structured command."""
        if not message or not message.strip():
            return ParsedCommand(action="unknown", entity="", params={}, raw_text=message or "")

        text = message.strip()

        for pattern, action, entity in cls.PATTERNS:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                params = cls._extract_params(action, entity, groups, text)
                return ParsedCommand(action=action, entity=entity, params=params, raw_text=text)

        return ParsedCommand(action="unknown", entity="", params={"message": text}, raw_text=text)

    @classmethod
    def _extract_params(cls, action: str, entity: str, groups: tuple, raw: str) -> Dict[str, Any]:
        """Extract parameters based on the action type."""
        params: Dict[str, Any] = {}

        if action == "create" and entity == "task":
            content = groups[0] if groups else ""
            params.update(cls._parse_task_creation(content))

        elif action == "update":
            params["taskId"] = groups[0] if groups else ""
            if len(groups) > 1:
                params.update(cls._parse_update_fields(groups[1]))

        elif action in ("delete", "complete", "get_one"):
            params["taskId"] = groups[0] if groups else ""

        elif action == "search":
            params["query"] = groups[0] if groups else ""

        elif action == "search_tag":
            params["tag"] = groups[0] if groups else ""

        elif action == "filter_priority":
            params["priority"] = (groups[0] if groups else "").upper()

        elif action == "filter_status":
            status_map = {
                "todo": "TO_DO", "to-do": "TO_DO", "pending": "TO_DO",
                "in-progress": "IN_PROGRESS", "active": "IN_PROGRESS", "started": "IN_PROGRESS",
                "done": "DONE", "completed": "DONE", "finished": "DONE",
            }
            raw_status = (groups[0] if groups else "").lower()
            params["status"] = status_map.get(raw_status, raw_status.upper())

        elif action == "sort":
            params["sortBy"] = groups[0] if groups else "createdAt"
            params["sortOrder"] = groups[1] if len(groups) > 1 and groups[1] else "asc"

        elif action == "create" and entity == "recurring-task":
            params.update(cls._parse_recurring_task(groups[0] if groups else ""))

        elif action == "create" and entity == "reminder":
            params["details"] = groups[0] if groups else ""

        return params

    @classmethod
    def _parse_task_creation(cls, content: str) -> Dict[str, Any]:
        """Parse task creation content for title, priority, tags, due date."""
        params: Dict[str, Any] = {"title": content}

        # Extract priority
        priority_match = re.search(r"priority[:\s]+(\w+)", content, re.IGNORECASE)
        if priority_match:
            params["priority"] = priority_match.group(1).upper()
            params["title"] = re.sub(r"\s*priority[:\s]+\w+", "", params["title"], flags=re.IGNORECASE).strip()

        # Extract tags
        tag_match = re.search(r"(?:tags?|tagged?)[:\s]+([\w\s,\-]+?)(?:\s+(?:priority|due)|$)", content, re.IGNORECASE)
        if tag_match:
            tags_str = tag_match.group(1)
            params["tags"] = [t.strip() for t in tags_str.split(",") if t.strip()]
            params["title"] = re.sub(r"\s*(?:tags?|tagged?)[:\s]+[\w\s,\-]+", "", params["title"], flags=re.IGNORECASE).strip()

        # Extract due date phrase
        due_match = re.search(r"(?:due|by|before)[:\s]+(.+?)(?:\s+(?:priority|tags?)|$)", content, re.IGNORECASE)
        if due_match:
            params["dueDate"] = due_match.group(1).strip()
            params["title"] = re.sub(r"\s*(?:due|by|before)[:\s]+.+?(?:\s+(?:priority|tags?)|$)", "", params["title"], flags=re.IGNORECASE).strip()

        # Clean title
        params["title"] = params["title"].strip(" :,")
        return params

    @classmethod
    def _parse_update_fields(cls, fields_str: str) -> Dict[str, Any]:
        """Parse update fields from a string like 'priority: high status: done'."""
        updates: Dict[str, Any] = {}

        for field_match in re.finditer(r"(\w+)[:\s]+([^\s:]+(?:\s+[^\s:]+)*?)(?=\s+\w+[:\s]|$)", fields_str):
            key = field_match.group(1).lower()
            value = field_match.group(2).strip()

            if key == "priority":
                updates["priority"] = value.upper()
            elif key == "status":
                updates["status"] = value.upper().replace("-", "_")
            elif key == "title":
                updates["title"] = value
            elif key in ("description", "desc"):
                updates["description"] = value
            elif key in ("due", "duedate"):
                updates["dueDate"] = value

        return updates

    @classmethod
    def _parse_recurring_task(cls, content: str) -> Dict[str, Any]:
        """Parse recurring task creation content."""
        params: Dict[str, Any] = {"title": content}

        # Extract pattern: "every Monday", "daily", "weekly", "monthly"
        pattern_match = re.search(r"every\s+(\w+)(?:\s+at\s+(\d{1,2}(?::\d{2})?(?:\s*[ap]m)?))?", content, re.IGNORECASE)
        if pattern_match:
            freq = pattern_match.group(1).lower()
            time_str = pattern_match.group(2)
            day_map = {
                "monday": 1, "tuesday": 2, "wednesday": 3,
                "thursday": 4, "friday": 5, "saturday": 6, "sunday": 0,
                "day": None, "week": None, "month": None, "year": None,
            }
            if freq in day_map and day_map[freq] is not None:
                params["recurrenceType"] = "WEEKLY"
                params["daysOfWeek"] = [day_map[freq]]
            elif freq in ("day", "daily"):
                params["recurrenceType"] = "DAILY"
            elif freq in ("week", "weekly"):
                params["recurrenceType"] = "WEEKLY"
            elif freq in ("month", "monthly"):
                params["recurrenceType"] = "MONTHLY"
            elif freq in ("year", "yearly"):
                params["recurrenceType"] = "YEARLY"

            if time_str:
                params["startTime"] = time_str

            params["title"] = re.sub(r"\s*every\s+\w+(?:\s+at\s+\S+)?", "", params["title"], flags=re.IGNORECASE).strip()

        params["title"] = params["title"].strip(" :,")
        return params
