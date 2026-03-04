# Data Model: Event-Driven, Cloud-Native Todo Chatbot

**Date**: 2026-01-16
**Feature**: Event-Driven, Cloud-Native Todo Chatbot
**Branch**: 001-event-driven-todo-chatbot

## Overview

This document defines the data models for the event-driven todo chatbot system. The models are designed to support the functional requirements while maintaining compatibility with the event-driven architecture and Dapr state management patterns.

## Core Entities

### 1. User

**Description**: Represents a system user with authentication and preferences

**Fields**:
- `userId` (UUID, required): Unique identifier for the user
- `username` (String, required): User's display name (max 50 chars)
- `email` (String, required): User's email address (valid email format)
- `createdAt` (ISO8601, required): Timestamp when user was created
- `updatedAt` (ISO8601, required): Timestamp when user was last updated
- `preferences` (JSON, optional): User preferences including timezone

**Relationships**:
- Has many Tasks
- Has many RecurringTasks

**Validation Rules**:
- Email must be valid email format
- Username must be 3-50 alphanumeric characters with underscores/hyphens
- userId must be unique across system

### 2. Task

**Description**: Represents a single task with properties and state

**Fields**:
- `taskId` (UUID, required): Unique identifier for the task
- `userId` (UUID, required): Reference to owning user
- `title` (String, required): Task title (max 200 chars)
- `description` (String, optional): Detailed task description (max 2000 chars)
- `dueDate` (ISO8601, optional): Date/time when task is due
- `priority` (Enum, required): Priority level (HIGH, MEDIUM, LOW)
- `status` (Enum, required): Current status (TO_DO, IN_PROGRESS, DONE)
- `tags` (Array<String>, optional): Array of tags (max 5 items, max 50 chars each)
- `createdAt` (ISO8601, required): Timestamp when task was created
- `updatedAt` (ISO8601, required): Timestamp when task was last updated
- `completedAt` (ISO8601, optional): Timestamp when task was completed
- `recurrencePattern` (JSON, optional): Pattern for recurring tasks

**Relationships**:
- Belongs to User
- May have associated Reminder
- May be generated from RecurringTask

**Validation Rules**:
- Title must be 1-200 characters
- Priority must be one of HIGH, MEDIUM, LOW
- Status must be one of TO_DO, IN_PROGRESS, DONE
- Tags array must not exceed 5 items
- Each tag must be 1-50 alphanumeric characters with spaces/hyphens
- dueDate must be in future if provided

### 3. RecurringTask

**Description**: Template for tasks that repeat on a schedule

**Fields**:
- `recurringTaskId` (UUID, required): Unique identifier for the recurring task
- `userId` (UUID, required): Reference to owning user
- `title` (String, required): Template title (max 200 chars)
- `description` (String, optional): Template description (max 2000 chars)
- `priority` (Enum, required): Default priority (HIGH, MEDIUM, LOW)
- `pattern` (JSON, required): Recurrence pattern definition
  - `type` (Enum): RECURRENCE_TYPE (DAILY, WEEKLY, MONTHLY, YEARLY)
  - `interval` (Integer): How often to repeat (positive integer)
  - `daysOfWeek` (Array<Integer>, optional): Days of week (0=Sunday, 6=Saturday) for weekly patterns
  - `dayOfMonth` (Integer, optional): Day of month for monthly patterns
  - `month` (Integer, optional): Month (1-12) for yearly patterns
  - `startTime` (String, optional): Start time in HH:MM format
- `isActive` (Boolean, required): Whether the pattern is currently active
- `endDate` (ISO8601, optional): Date when recurrence stops
- `createdAt` (ISO8601, required): Timestamp when template was created
- `updatedAt` (ISO8601, required): Timestamp when template was last updated

**Relationships**:
- Belongs to User
- Generates many Tasks

**Validation Rules**:
- Title must be 1-200 characters
- Priority must be one of HIGH, MEDIUM, LOW
- Pattern must be valid recurrence configuration
- endDate must be in future if provided
- startTime must be valid HH:MM format

### 4. Reminder

**Description**: Scheduled notification for task deadlines

**Fields**:
- `reminderId` (UUID, required): Unique identifier for the reminder
- `taskId` (UUID, required): Reference to associated task
- `userId` (UUID, required): Reference to user who owns the task
- `scheduledTime` (ISO8601, required): When the reminder should be sent
- `status` (Enum, required): Current status (SCHEDULED, SENT, FAILED)
- `method` (Enum, required): How the reminder is delivered (CHAT, EMAIL, PUSH)
- `createdAt` (ISO8601, required): Timestamp when reminder was created
- `sentAt` (ISO8601, optional): Timestamp when reminder was sent
- `failureReason` (String, optional): Reason for failure if status is FAILED

**Relationships**:
- Belongs to Task
- Belongs to User

**Validation Rules**:
- scheduledTime must be in future
- status must be one of SCHEDULED, SENT, FAILED
- method must be one of CHAT, EMAIL, PUSH

### 5. TaskEvent

**Description**: Event representing changes to tasks in the system

**Fields**:
- `eventId` (UUID, required): Unique identifier for the event
- `eventType` (String, required): Type of event (task.created, task.updated, task.deleted, task.completed)
- `taskId` (UUID, required): Reference to the affected task
- `userId` (UUID, required): Reference to user who triggered the event
- `timestamp` (ISO8601, required): When the event occurred
- `previousData` (JSON, optional): Previous state for update events
- `newData` (JSON, required): New state of the task
- `correlationId` (UUID, optional): ID to correlate related events

**Validation Rules**:
- eventType must be one of the defined event types
- timestamp must be current or past
- newData must contain valid task data

## Database Schema

### PostgreSQL Tables

#### users
```sql
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  preferences JSONB
);

CREATE INDEX idx_users_email ON users(email);
```

#### tasks
```sql
CREATE TABLE tasks (
  task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(user_id),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  due_date TIMESTAMP WITH TIME ZONE,
  priority VARCHAR(10) NOT NULL CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')),
  status VARCHAR(15) NOT NULL CHECK (status IN ('TO_DO', 'IN_PROGRESS', 'DONE')),
  tags TEXT[],
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  recurrence_pattern JSONB,

  CONSTRAINT chk_tags_count CHECK (array_length(tags, 1) <= 5)
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
```

#### recurring_tasks
```sql
CREATE TABLE recurring_tasks (
  recurring_task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(user_id),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  priority VARCHAR(10) NOT NULL CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')),
  pattern JSONB NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  end_date TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_recurring_tasks_user_id ON recurring_tasks(user_id);
CREATE INDEX idx_recurring_tasks_is_active ON recurring_tasks(is_active);
```

#### reminders
```sql
CREATE TABLE reminders (
  reminder_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID NOT NULL REFERENCES tasks(task_id),
  user_id UUID NOT NULL REFERENCES users(user_id),
  scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
  status VARCHAR(15) NOT NULL CHECK (status IN ('SCHEDULED', 'SENT', 'FAILED')),
  method VARCHAR(10) NOT NULL CHECK (method IN ('CHAT', 'EMAIL', 'PUSH')),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  sent_at TIMESTAMP WITH TIME ZONE,
  failure_reason TEXT
);

CREATE INDEX idx_reminders_task_id ON reminders(task_id);
CREATE INDEX idx_reminders_user_id ON reminders(user_id);
CREATE INDEX idx_reminders_scheduled_time ON reminders(scheduled_time);
CREATE INDEX idx_reminders_status ON reminders(status);
```

#### task_events
```sql
CREATE TABLE task_events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type VARCHAR(50) NOT NULL,
  task_id UUID NOT NULL,
  user_id UUID NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  previous_data JSONB,
  new_data JSONB NOT NULL,
  correlation_id UUID
);

CREATE INDEX idx_task_events_task_id ON task_events(task_id);
CREATE INDEX idx_task_events_user_id ON task_events(user_id);
CREATE INDEX idx_task_events_timestamp ON task_events(timestamp);
CREATE INDEX idx_task_events_event_type ON task_events(event_type);
```

## Relationships

```
Users 1 ---- * Tasks
Users 1 ---- * RecurringTasks
Users 1 ---- * Reminders
Tasks 1 ---- * Reminders
Tasks 1 ---- * TaskEvents
RecurringTasks 1 ---- * Tasks (generated)
```

## State Transitions

### Task Status Transitions
- TO_DO → IN_PROGRESS (when user starts working on task)
- IN_PROGRESS → TO_DO (when user returns task to to-do)
- IN_PROGRESS → DONE (when user completes task)
- TO_DO → DONE (when user marks unstarted task as complete)

### Reminder Status Transitions
- SCHEDULED → SENT (when reminder is successfully delivered)
- SCHEDULED → FAILED (when reminder delivery fails)
- SENT → FAILED (in rare cases where delivery confirmation fails)

## Indexing Strategy

Primary indexes are created on foreign keys and frequently queried fields to ensure optimal query performance for the specified search and filter requirements.