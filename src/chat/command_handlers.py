"""Chat command handlers for the todo chatbot application."""

import logging
from typing import Dict, Any, Optional

from src.chat.command_parser import ParsedCommand
from src.services.task_service import TaskService
from src.services.task_event_service import TaskEventService
from src.services.validation import TaskValidator, ValidationError
from src.models.task import Task
from src.utils.constants import TaskPriority, TaskStatus, EventType

logger = logging.getLogger(__name__)

task_service = TaskService()
event_service = TaskEventService()


class CommandHandlers:
    """Handles parsed chat commands and executes corresponding operations."""

    @classmethod
    async def handle(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Route a parsed command to the appropriate handler."""
        handlers = {
            "create": cls.handle_create_task,
            "update": cls.handle_update_task,
            "get": cls.handle_get_tasks,
            "get_one": cls.handle_get_task,
            "delete": cls.handle_delete_task,
            "complete": cls.handle_complete_task,
            "search": cls.handle_search_tasks,
            "search_tag": cls.handle_search_by_tag,
            "filter_priority": cls.handle_filter_by_priority,
            "filter_status": cls.handle_filter_by_status,
            "sort": cls.handle_sort_tasks,
            "help": cls.handle_help,
        }

        handler = handlers.get(command.action)
        if not handler:
            return {
                "response": "I didn't understand that command. Type 'help' to see available commands.",
                "action": "unknown",
                "data": None,
            }

        return await handler(command, user_id)

    @classmethod
    async def handle_create_task(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Handle 'create task' command."""
        try:
            params = command.params
            priority = params.get("priority", "MEDIUM")
            tags = params.get("tags", [])

            validated = TaskValidator.validate_create_task({
                "title": params.get("title", ""),
                "description": params.get("description"),
                "dueDate": params.get("dueDate"),
                "priority": priority,
                "status": "TO_DO",
                "tags": tags,
            })

            task = Task(
                userId=user_id,
                title=validated["title"],
                description=validated["description"],
                dueDate=validated["dueDate"],
                priority=TaskPriority(validated["priority"]),
                status=TaskStatus(validated["status"]),
                tags=validated["tags"],
            )

            created = await task_service.create_task(task)
            await event_service.publish_task_created(created)

            return {
                "response": f"Task created: '{created.title}' (ID: {created.taskId})",
                "action": "task.created",
                "data": created.to_dict(),
            }
        except ValidationError as e:
            return {"response": f"Validation error: {e}", "action": "error", "data": None}
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return {"response": f"Failed to create task: {e}", "action": "error", "data": None}

    @classmethod
    async def handle_update_task(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Handle 'update task' command."""
        try:
            task_id = command.params.get("taskId", "")
            update_fields = {k: v for k, v in command.params.items() if k != "taskId"}

            if not update_fields:
                return {"response": "No fields to update specified.", "action": "error", "data": None}

            validated = TaskValidator.validate_update_task(update_fields)

            previous_task = await task_service.get_task_by_id(task_id, user_id)
            if not previous_task:
                return {"response": f"Task #{task_id} not found.", "action": "error", "data": None}

            previous_data = previous_task.to_dict()
            updated = await task_service.update_task(task_id, user_id, validated)
            if not updated:
                return {"response": f"Task #{task_id} not found.", "action": "error", "data": None}

            await event_service.publish_task_updated(updated, previous_data)

            return {
                "response": f"Task #{task_id} updated successfully.",
                "action": "task.updated",
                "data": updated.to_dict(),
            }
        except ValidationError as e:
            return {"response": f"Validation error: {e}", "action": "error", "data": None}
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return {"response": f"Failed to update task: {e}", "action": "error", "data": None}

    @classmethod
    async def handle_get_tasks(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Handle 'get tasks' command."""
        try:
            tasks = await task_service.get_tasks_by_user(user_id, limit=20)
            if not tasks:
                return {"response": "You have no tasks.", "action": "tasks.listed", "data": []}

            lines = [f"Your tasks ({len(tasks)} total):"]
            for t in tasks:
                priority = t.priority.value if hasattr(t.priority, 'value') else t.priority
                status = t.status.value if hasattr(t.status, 'value') else t.status
                lines.append(f"  - [{status}] {t.title} (Priority: {priority}, ID: {t.taskId[:8]}...)")

            return {
                "response": "\n".join(lines),
                "action": "tasks.listed",
                "data": [t.to_dict() for t in tasks],
            }
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return {"response": f"Failed to retrieve tasks: {e}", "action": "error", "data": None}

    @classmethod
    async def handle_get_task(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Handle 'get task #ID' command."""
        try:
            task_id = command.params.get("taskId", "")
            task = await task_service.get_task_by_id(task_id, user_id)
            if not task:
                return {"response": f"Task #{task_id} not found.", "action": "error", "data": None}

            priority = task.priority.value if hasattr(task.priority, 'value') else task.priority
            status = task.status.value if hasattr(task.status, 'value') else task.status
            lines = [
                f"Task: {task.title}",
                f"  ID: {task.taskId}",
                f"  Status: {status}",
                f"  Priority: {priority}",
            ]
            if task.description:
                lines.append(f"  Description: {task.description}")
            if task.dueDate:
                lines.append(f"  Due: {task.dueDate}")
            if task.tags:
                lines.append(f"  Tags: {', '.join(task.tags)}")

            return {
                "response": "\n".join(lines),
                "action": "task.retrieved",
                "data": task.to_dict(),
            }
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return {"response": f"Failed to retrieve task: {e}", "action": "error", "data": None}

    @classmethod
    async def handle_delete_task(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Handle 'delete task' command."""
        try:
            task_id = command.params.get("taskId", "")
            task = await task_service.get_task_by_id(task_id, user_id)
            if not task:
                return {"response": f"Task #{task_id} not found.", "action": "error", "data": None}

            deleted = await task_service.delete_task(task_id, user_id)
            if not deleted:
                return {"response": f"Task #{task_id} not found.", "action": "error", "data": None}

            await event_service.publish_task_deleted(task)

            return {
                "response": f"Task '{task.title}' deleted.",
                "action": "task.deleted",
                "data": {"taskId": task_id},
            }
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return {"response": f"Failed to delete task: {e}", "action": "error", "data": None}

    @classmethod
    async def handle_complete_task(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Handle 'complete task' command."""
        try:
            task_id = command.params.get("taskId", "")
            previous_task = await task_service.get_task_by_id(task_id, user_id)
            if not previous_task:
                return {"response": f"Task #{task_id} not found.", "action": "error", "data": None}

            previous_data = previous_task.to_dict()
            completed = await task_service.complete_task(task_id, user_id)
            if not completed:
                return {"response": f"Task #{task_id} not found.", "action": "error", "data": None}

            await event_service.publish_task_completed(completed, previous_data)

            return {
                "response": f"Task '{completed.title}' marked as done!",
                "action": "task.completed",
                "data": completed.to_dict(),
            }
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return {"response": f"Failed to complete task: {e}", "action": "error", "data": None}

    @classmethod
    async def handle_search_tasks(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Handle 'search tasks' command."""
        query = command.params.get("query", "")
        return {
            "response": f"Searching tasks for: '{query}' (search service not yet integrated)",
            "action": "tasks.search",
            "data": {"query": query},
        }

    @classmethod
    async def handle_search_by_tag(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Handle 'search tasks tagged:X' command."""
        tag = command.params.get("tag", "")
        return {
            "response": f"Searching tasks tagged: '{tag}' (search service not yet integrated)",
            "action": "tasks.search_tag",
            "data": {"tag": tag},
        }

    @classmethod
    async def handle_filter_by_priority(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Handle 'show high priority tasks' command."""
        priority = command.params.get("priority", "")
        return {
            "response": f"Filtering tasks by priority: {priority} (search service not yet integrated)",
            "action": "tasks.filter_priority",
            "data": {"priority": priority},
        }

    @classmethod
    async def handle_filter_by_status(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Handle 'show done tasks' command."""
        try:
            status_value = command.params.get("status", "")
            try:
                task_status = TaskStatus(status_value)
            except ValueError:
                return {"response": f"Unknown status: {status_value}", "action": "error", "data": None}

            tasks = await task_service.get_tasks_by_status(user_id, task_status)
            if not tasks:
                return {"response": f"No {status_value} tasks found.", "action": "tasks.filtered", "data": []}

            lines = [f"{status_value} tasks ({len(tasks)}):"]
            for t in tasks:
                lines.append(f"  - {t.title} (ID: {t.taskId[:8]}...)")

            return {
                "response": "\n".join(lines),
                "action": "tasks.filtered",
                "data": [t.to_dict() for t in tasks],
            }
        except Exception as e:
            logger.error(f"Error filtering tasks: {e}")
            return {"response": f"Failed to filter tasks: {e}", "action": "error", "data": None}

    @classmethod
    async def handle_sort_tasks(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Handle 'sort tasks by X' command."""
        sort_by = command.params.get("sortBy", "createdAt")
        sort_order = command.params.get("sortOrder", "asc")
        return {
            "response": f"Sorting tasks by {sort_by} ({sort_order}) (search service not yet integrated)",
            "action": "tasks.sort",
            "data": {"sortBy": sort_by, "sortOrder": sort_order},
        }

    @classmethod
    async def handle_help(cls, command: ParsedCommand, user_id: str) -> Dict[str, Any]:
        """Handle 'help' command."""
        help_text = """Available commands:
  - create task: <title> [priority: high/medium/low] [tags: tag1, tag2]
  - update task #<id> <field>: <value>
  - delete task #<id>
  - complete task #<id>
  - show tasks / list tasks
  - show task #<id>
  - show <status> tasks (e.g., show done tasks)
  - show <priority> priority tasks
  - search tasks <query>
  - search tasks tagged: <tag>
  - sort tasks by <field> [asc/desc]
  - create recurring task: <title> every <day/week/month>
  - schedule reminder <details>
  - help"""

        return {
            "response": help_text,
            "action": "help",
            "data": None,
        }
