"""SearchService for task search, filter, and sort functionality."""

import logging
from typing import Optional, List, Dict, Any

from src.models.task import Task
from src.utils.database import db_pool
from src.utils.constants import TaskPriority, TaskStatus
from src.utils.helpers import is_valid_uuid

logger = logging.getLogger(__name__)


class SearchService:
    """Service class for searching, filtering, and sorting tasks."""

    VALID_SORT_FIELDS = {"dueDate": "due_date", "createdAt": "created_at", "priority": "priority", "title": "title"}

    async def search_tasks(
        self,
        user_id: str,
        query: Optional[str] = None,
        tag: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = "createdAt",
        sort_order: Optional[str] = "desc",
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Search tasks with filtering and sorting."""
        if not is_valid_uuid(user_id):
            raise ValueError("Invalid user ID format")

        conditions = ["user_id = $1"]
        params: list = [user_id]
        param_idx = 2

        # Full-text search
        if query:
            conditions.append(f"to_tsvector('english', title || ' ' || COALESCE(description, '')) @@ plainto_tsquery('english', ${param_idx})")
            params.append(query)
            param_idx += 1

        # Tag filter
        if tag:
            conditions.append(f"${param_idx} = ANY(tags)")
            params.append(tag)
            param_idx += 1

        # Priority filter
        if priority:
            conditions.append(f"priority = ${param_idx}")
            params.append(priority.upper())
            param_idx += 1

        # Status filter
        if status:
            conditions.append(f"status = ${param_idx}")
            params.append(status.upper())
            param_idx += 1

        where_clause = " AND ".join(conditions)

        # Sort
        sort_col = self.VALID_SORT_FIELDS.get(sort_by, "created_at")
        order = "ASC" if sort_order and sort_order.lower() == "asc" else "DESC"

        # Count
        count_query = f"SELECT COUNT(*) FROM tasks WHERE {where_clause}"
        async with db_pool.get_db_connection() as conn:
            total = await conn.fetchval(count_query, *params)

        # Fetch
        offset = (page - 1) * limit
        data_query = f"""
            SELECT task_id, user_id, title, description, due_date, priority, status,
                   tags, created_at, updated_at, completed_at, recurrence_pattern
            FROM tasks WHERE {where_clause}
            ORDER BY {sort_col} {order}
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """
        params.extend([limit, offset])

        async with db_pool.get_db_connection() as conn:
            results = await conn.fetch(data_query, *params)

        tasks = []
        for r in results:
            task = Task(
                taskId=str(r['task_id']),
                userId=str(r['user_id']),
                title=r['title'],
                description=r['description'],
                dueDate=r['due_date'].isoformat() + 'Z' if r['due_date'] else None,
                priority=TaskPriority(r['priority']),
                status=TaskStatus(r['status']),
                tags=r['tags'] if r['tags'] else [],
                createdAt=r['created_at'].isoformat() + 'Z',
                updatedAt=r['updated_at'].isoformat() + 'Z',
                completedAt=r['completed_at'].isoformat() + 'Z' if r['completed_at'] else None,
                recurrencePattern=r['recurrence_pattern'],
            )
            tasks.append(task.to_dict())

        total_pages = (total + limit - 1) // limit if total else 0

        return {
            "tasks": tasks,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": total_pages,
            },
        }
