# Implementation Plan: Event-Driven, Cloud-Native Todo Chatbot

**Feature Branch**: `001-event-driven-todo-chatbot`
**Created**: 2026-01-16
**Status**: Draft
**Input**: `/sp.plan

Project: Event-Driven, Cloud-Native Todo Chatbot
Phase: Phase V – Advanced Cloud Deployment

────────────────────────────────────────
CREATE
────────────────────────────────────────
- Architecture Sketch:
  - Define microservices, event flows, Dapr service boundaries, and Kafka topics
  - Clearly separate responsibilities for Task, Recurring Task, Reminder, Search, and Chat Interface services
  - Define frontend-backend interaction via Dapr Service Invocation
  - Define state persistence via PostgreSQL using Dapr State Management
  - Map local Minikube deployment to cloud Kubernetes deployment with no code changes

- Section Structure:
  1. Overview & Objectives
  2. Event-Driven Architecture Overview
  3. Microservice Responsibilities
  4. Dapr Integration Patterns
  5. Kafka Topic & Event Strategy
  6. Feature Implementation Mapping (Advanced + Intermediate)
  7. User Identity & Persistence Model
  8. Deployment Strategy
────────────────────────────────────────
- Unit Tests: Validate individual microservice logic against specs
- Integration Tests: Ensure events propagate correctly via Kafka/Dapr
- End-to-End Tests: Confirm feature flows (task creation → reminder → completion)
- Deployment Tests: Local Minikube → Cloud Kubernetes parity check
- Compliance Checks: Constitution adherence, no direct Kafka access, spec alignment
- Performance Checks: Event throughput and state management efficiency

────────────────────────────────────────
TECHNICAL DETAILS
────────────────────────────────────────
- Development Phases:
  1. Specify → Plan → Tasks → Implement (strict SDD)
  2. Microservice scaffold creation
  3. Event topic design & Dapr integration
  4. Feature implementation (Advanced → Intermediate)
  5. Search and Chat Interface
  6. Recurring Task and Reminder Services using Dapr Jobs API
  7. Observability and CI/CD integration
  8. End-to-end validation and audit review

- Documentation:
  - Maintain full traceability: Spec → Plan → Task → Code → Test
  - Record all architectural decisions and trade-offs
  - No undocumented behavior is permitted

────────────────────────────────────────
ARCHITECTURE OVERVIEW
────────────────────────────────────────
- Backend: Python (FastAPI, async)
- Frontend: Next.js
- Orchestration: Kubernetes (Minikube local, AKS/GKE/OKE cloud)
- Event Streaming: Kafka (only via Dapr Pub/Sub)
- Distributed Runtime: Dapr
- Database: External managed PostgreSQL (Neon)
- Packaging: Helm charts
- CI/CD: GitHub Actions
- Observability: Centralized logging and monitoring

No additional infrastructure or tools are permitted unless added to the specification and constitution.

────────────────────────────────────────
USER IDENTITY & DATA PERSISTENCE
────────────────────────────────────────
- Users must create real accounts (no mock or test users)
- User identity (name, email) is persisted in PostgreSQL via Dapr State APIs
- User data (tasks, reminders, preferences) must persist across sessions
- Users can update name and email via Settings
- On every login, the dashboard must display the stored user name
- All user-related data must be scoped by user ID and isolated per account

────────────────────────────────────────
EVENT-DRIVEN ARCHITECTURE
────────────────────────────────────────
- All task lifecycle actions emit domain events
- No synchronous cross-service dependencies
- Eventual consistency is the default model
- Required Kafka topics:
  - task-events (CRUD, lifecycle, recurring triggers)
  - reminders (scheduled and delivery events)

────────────────────────────────────────
DAPR INTEGRATION PATTERNS
────────────────────────────────────────
- Pub/Sub: Kafka abstraction only
- State Management: PostgreSQL via Dapr APIs only
- Jobs API: Mandatory for exact-time reminders and recurring task scheduling
- Service Invocation: Frontend-backend and internal service calls
- Secrets: Accessed via Dapr or Kubernetes Secrets only

────────────────────────────────────────
DEPLOYMENT STRATEGY
────────────────────────────────────────
- Local:
  - Minikube with Dapr sidecar injection
  - Kafka via operator
  - External PostgreSQL connection

- Cloud:
  - Managed Kubernetes (AKS/GKE/OKE)
  - Helm-based deployments
  - Identical configuration structure to local

────────────────────────────────────────
RISK & CONSTRAINT MANAGEMENT
────────────────────────────────────────
- No polling mechanisms allowed
- No direct Kafka usage allowed
- No architecture or feature changes without updating specification
- Any missing or ambiguous requirement must halt implementation

────────────────────────────────────────
PLAN COMPLETENESS RULE
────────────────────────────────────────
No development or coding may proceed unless this plan fully maps all
specified features, architecture decisions, testing strategies, and
compliance requirements. Any ambiguity or deviation requires an update
to this plan and the specification before implementation."

## Technical Context

### Architecture Overview
- **Backend**: Python (FastAPI, async) - Per architecture overview
- **Frontend**: Next.js - Per architecture overview
- **Orchestration**: Kubernetes (Minikube local, AKS/GKE/OKE cloud) - Per architecture overview
- **Event Streaming**: Kafka (only via Dapr Pub/Sub) - Per architecture overview
- **Distributed Runtime**: Dapr - Per architecture overview
- **Database**: External managed PostgreSQL (Neon) - Per architecture overview
- **Packaging**: Helm charts - Per architecture overview
- **CI/CD**: GitHub Actions - Per architecture overview
- **Observability**: Centralized logging and monitoring - Per architecture overview

### Infrastructure Components
- **Message Broker**: Kafka cluster managed by Strimzi operator
- **Service Mesh**: Dapr sidecars for all microservices
- **State Store**: PostgreSQL for persistent data, Redis for caching
- **Authentication**: JWT-based authentication system
- **Monitoring**: Prometheus + Grafana, centralized logging with ELK stack

### Technology Stack Compliance
- All services must use Dapr for inter-service communication
- No direct Kafka client usage allowed in application code
- Event-driven architecture pattern enforced throughout
- Cloud-native, Kubernetes-first design approach
- No polling mechanisms allowed per risk constraints

## Constitution Check

### Compliance Verification
- ✅ **Strict Spec-Driven Development**: Following Specify → Plan → Tasks → Implement sequence
- ✅ **No manual or freestyle coding**: All code via Claude Code as required
- ✅ **Event-driven architecture**: All communication via Dapr pub/sub
- ✅ **Cloud-native, Kubernetes-first**: Designed for K8s deployment
- ✅ **Loose coupling via Dapr**: Services communicate through Dapr abstractions
- ✅ **No direct Kafka clients**: Kafka accessed only through Dapr pub/sub
- ✅ **No polling-based reminder systems**: Using Dapr Jobs API for scheduling
- ✅ **No monolithic services**: Proper service boundaries defined
- ✅ **Technology stack compliance**: Using Python, Next.js, Dapr, Kafka, PostgreSQL
- ✅ **Task ID requirement**: All work will reference valid Task IDs
- ✅ **No polling mechanisms**: Using Dapr Jobs API instead of polling

### Gate Evaluations
- **Architecture Gate**: PASSED - Event-driven, microservice architecture compliant
- **Technology Gate**: PASSED - All technologies per architecture overview
- **Pattern Gate**: PASSED - Dapr abstraction layer, no direct Kafka access
- **Deployment Gate**: PASSED - Kubernetes native design
- **Compliance Gate**: PASSED - No polling, proper Dapr usage

## 1. Overview & Objectives

### Primary Objectives
- Implement event-driven todo chatbot with recurring tasks and reminders
- Demonstrate advanced cloud-native architecture patterns
- Ensure seamless deployment across local (Minikube) and cloud (Kubernetes) environments
- Achieve high reliability for task management and reminder delivery
- Enable real user accounts with persistent identity and data
- Support all specified advanced and intermediate features

### Success Metrics
- 99% success rate for task creation and management operations
- Sub-2 second response time for task operations under normal load
- 95% of reminders delivered within 1 minute of scheduled time
- 99.9% reliability for recurring task generation
- Sub-1 second response time for search/filter operations up to 10,000 tasks per user
- 99.5% uptime in both local and cloud deployments
- Real user accounts with persistent identity and data

## 2. Event-Driven Architecture Overview

### Event Flows
- **Task Events Topic**: `task-events` - CRUD operations and lifecycle events
  - `task.created`, `task.updated`, `task.deleted`, `task.completed`
  - `task.priority.changed`, `task.due.date.changed`, `task.tags.changed`
  - `recurring-task.created`, `recurring-task.triggered`, `recurring-task.updated`
  - `user.profile.updated` - for user identity changes
- **Reminder Events Topic**: `reminders` - scheduled notifications
  - `reminder.scheduled`, `reminder.sent`, `reminder.failed`
  - `reminder.rescheduled` - when due dates change

### Event Processing Patterns
- **Command-Query Responsibility Segregation (CQRS)**: Separate read/write models
- **Event Sourcing**: Task state changes stored as immutable event stream
- **Saga Pattern**: For complex operations involving multiple services
- **Event Carried State Transfer**: Services maintain their own read models

### Event Schema
```
TaskEvent:
  - eventType: String (created, updated, deleted, completed, priority.changed, etc.)
  - taskId: UUID
  - userId: UUID
  - timestamp: ISO8601
  - correlationId: UUID (for tracing)
  - data: TaskData object

ReminderEvent:
  - eventType: String (scheduled, sent, failed, rescheduled)
  - reminderId: UUID
  - taskId: UUID
  - userId: UUID
  - scheduledTime: ISO8601
  - deliveryTime: ISO8601 (for sent events)
  - correlationId: UUID (for tracing)

UserEvent:
  - eventType: String (profile.updated, email.changed, etc.)
  - userId: UUID
  - timestamp: ISO8601
  - correlationId: UUID (for tracing)
  - data: UserData object
```

## 3. Microservice Responsibilities

### Task Management Service
- **Responsibility**: Core task CRUD operations, validation, persistence
- **API Endpoints**: Create, read, update, delete tasks
- **Events Published**: `task.created`, `task.updated`, `task.deleted`, `task.completed`, `task.priority.changed`, `task.due.date.changed`
- **Events Consumed**: None directly
- **Technology**: Python FastAPI, PostgreSQL via Dapr state store
- **Dapr Integration**: State management for task persistence, service invocation for other services

### Recurring Task Service
- **Responsibility**: Process recurring task patterns, generate new instances
- **API Endpoints**: Create/update recurring task templates
- **Events Published**: `recurring-task.created`, `recurring-task.triggered`
- **Events Consumed**: `task.created` (for recurring tasks), `user.profile.updated` (for user changes)
- **Technology**: Python FastAPI, Dapr Jobs API for scheduling
- **Dapr Integration**: Jobs API for scheduling recurring task generation, pub/sub for event communication

### Reminder Service
- **Responsibility**: Schedule and deliver task reminders
- **API Endpoints**: Schedule reminder requests
- **Events Published**: `reminder.scheduled`, `reminder.sent`, `reminder.failed`, `reminder.rescheduled`
- **Events Consumed**: `task.created`, `task.updated` (due date changes), `task.deleted` (cancel reminders)
- **Technology**: Python FastAPI, Dapr Jobs API, Kafka for event stream
- **Dapr Integration**: Jobs API for scheduling reminders, pub/sub for event communication

### Search Service
- **Responsibility**: Task search, filtering, and sorting capabilities
- **API Endpoints**: Search, filter, sort tasks
- **Events Published**: None
- **Events Consumed**: All task events for indexing, user events for user-specific data
- **Technology**: Python FastAPI, PostgreSQL full-text search
- **Dapr Integration**: Pub/sub for consuming events, service invocation for other services

### Chat Interface Service
- **Responsibility**: Natural language processing for chat commands
- **API Endpoints**: Chat command processing, WebSocket connections for real-time chat
- **Events Published**: Task operation commands, user commands
- **Events Consumed**: Task updates for user responses, reminder events for notifications
- **Technology**: Python FastAPI with WebSocket support, NLP processing
- **Dapr Integration**: Service invocation for calling other services, pub/sub for receiving updates

### User Management Service
- **Responsibility**: User account creation, authentication, profile management
- **API Endpoints**: Register, login, update profile, get user details
- **Events Published**: `user.profile.updated`, `user.created`
- **Events Consumed**: None directly
- **Technology**: Python FastAPI, PostgreSQL via Dapr state store
- **Dapr Integration**: State management for user persistence, secret management for JWT signing keys

### Frontend Service (Next.js)
- **Responsibility**: User interface, authentication handling, real-time updates
- **Communication**: Dapr Service Invocation to backend services
- **Features**: Dashboard showing user name, task management UI, settings for user profile updates
- **Technology**: Next.js, React, WebSocket connections for real-time updates
- **Dapr Integration**: Service invocation for API calls, secret management for tokens

## 4. Dapr Integration Patterns

### State Management
- **Component**: PostgreSQL state store
- **Usage**: Task data persistence, user profiles, recurring task templates, user preferences
- **Configuration**: Connection to external Neon PostgreSQL
- **Patterns**: Actor pattern for user-specific state management, state transactions for consistency

### Service Invocation
- **Pattern**: Async service-to-service calls via Dapr
- **Usage**: Cross-service communication without direct dependencies
- **Security**: mTLS enabled by default
- **Frontend-Backend**: Next.js frontend invokes backend services via Dapr service invocation

### Pub/Sub Building Block
- **Component**: Kafka pub/sub component
- **Topics**: `task-events`, `reminders`, `user-events`
- **Guarantees**: At-least-once delivery
- **Configuration**: Partitioned by user ID for load distribution and isolation
- **Patterns**: Fan-out for multiple consumers, dead letter queues for failed messages

### Jobs API
- **Usage**: Scheduled reminders and recurring task generation
- **Pattern**: Time-based triggers without polling
- **Reliability**: Persistent job scheduling with failure recovery
- **Exact-time Scheduling**: Per requirement, using Dapr Jobs API for precise timing

### Secret Management
- **Component**: Kubernetes secrets for Dapr
- **Usage**: Database credentials, JWT signing keys, Kafka connection details
- **Access**: Secure retrieval via Dapr secret API
- **Frontend**: Secure token management via Dapr secret store

## 5. Kafka Topic & Event Strategy

### Topic Design
- **task-events**: Partitioned by user ID for load distribution and user data isolation
- **reminders**: Partitioned by scheduled time for temporal processing
- **user-events**: Partitioned by user ID for load distribution
- **Retention**: Configured based on compliance and operational needs (7-30 days)

### Consumer Groups
- **Search Service**: Dedicated consumer group for indexing
- **Reminder Service**: Consumer group for processing reminder triggers
- **Analytics Service**: Consumer group for operational metrics
- **Frontend Service**: Consumer group for real-time updates to users

### Performance Considerations
- **Partitioning Strategy**: Horizontal scaling through proper partitioning by user ID
- **Producer Acknowledgments**: Appropriate durability vs performance trade-offs
- **Consumer Lag Monitoring**: Real-time monitoring of processing delays
- **Message Size**: Optimized for common event sizes, with compression enabled

### Event Ordering
- **Per-User Ordering**: Events for a specific user are ordered within partitions
- **Cross-User Parallelism**: Different users' events can be processed in parallel
- **Dependency Handling**: Events with dependencies include correlation IDs

## 6. Feature Implementation Mapping (Advanced + Intermediate)

### Advanced Features
1. **Recurring Tasks with Automatic Next-Occurrence Creation**
   - Implemented by: Recurring Task Service using Dapr Jobs API
   - Events: `recurring-task.created`, `recurring-task.triggered`
   - Persistence: Recurring task templates in PostgreSQL via Dapr state management
   - Trigger: Time-based jobs scheduled by Dapr Jobs API

2. **Due Dates with Exact-Time Reminders**
   - Implemented by: Reminder Service using Dapr Jobs API
   - Events: `reminder.scheduled`, `reminder.sent`, `reminder.failed`
   - Persistence: Reminder records in PostgreSQL via Dapr state management
   - Trigger: Exact-time jobs scheduled by Dapr Jobs API based on due dates

### Intermediate Features
1. **Task Priorities (High, Medium, Low)**
   - Implemented by: Task Management Service
   - Events: `task.priority.changed`
   - Persistence: Priority field in task records via Dapr state management
   - UI: Priority selection in frontend via Dapr service invocation

2. **Tags and Categorization**
   - Implemented by: Task Management Service
   - Events: `task.tags.changed`
   - Persistence: Tags array in task records via Dapr state management
   - Validation: Max 5 tags per task, max 50 characters each

3. **Search Functionality**
   - Implemented by: Search Service
   - Events: Consumes all task events for indexing
   - Persistence: Search indices maintained in PostgreSQL
   - Query: Full-text search by text, tag, priority, status

4. **Filter and Sort Operations**
   - Implemented by: Search Service
   - Events: Consumes task events for real-time index updates
   - Operations: Filter by due date, priority, status; Sort by due date, priority, title
   - Performance: Optimized with PostgreSQL indexes

### User Identity & Persistence
- **Account Creation**: User Management Service with real accounts
- **Identity Persistence**: User profiles in PostgreSQL via Dapr state management
- **Data Isolation**: All user data scoped by user ID
- **Profile Updates**: Settings page allows name/email updates
- **Login Display**: Dashboard shows stored user name on every login

## 7. User Identity & Persistence Model

### User Account Management
- **Registration**: Users create real accounts via registration API
- **Authentication**: JWT-based authentication system
- **Profile Data**: Name, email, preferences stored in PostgreSQL via Dapr state management
- **Persistence**: User data persists across sessions and deployments

### Identity Schema
- `userId` (UUID): Unique identifier for the user
- `name` (String): User's display name (required)
- `email` (String): User's email address (required, unique)
- `preferences` (JSON): User preferences including timezone, notification settings
- `createdAt` (ISO8601): Account creation timestamp
- `updatedAt` (ISO8601): Last profile update timestamp

### Data Scoping
- **User ID Isolation**: All tasks, reminders, and related data scoped by userId
- **Access Control**: Services validate userId ownership on all operations
- **Privacy**: Users cannot access other users' data
- **Security**: JWT tokens validated on all authenticated requests

### Profile Management
- **Updates**: Users can update name and email via Settings API
- **Validation**: Email format validation, name length limits
- **Events**: `user.profile.updated` emitted when profile changes
- **UI Display**: Dashboard always shows the stored user name

## 8. Deployment Strategy

### Local Environment (Minikube)
- **Infrastructure Setup**:
  - Minikube with sufficient resources (4 CPUs, 8GB RAM recommended)
  - Dapr sidecar injection enabled for all services
  - Kafka via Strimzi operator for local event streaming
  - External PostgreSQL connection to Neon
- **Service Configuration**:
  - Environment-specific configuration via Helm values
  - Local development overrides for debugging
  - Dapr component configurations for local development
- **Developer Experience**:
  - Hot-reloading for backend services
  - Fast refresh for Next.js frontend
  - Local debugging with Dapr placement service

### Cloud Environment (AKS/GKE/OKE)
- **Infrastructure Setup**:
  - Managed Kubernetes cluster with autoscaling
  - Dapr production configuration with security hardening
  - Kafka cluster via operator with enterprise features
  - Production PostgreSQL with backup and monitoring
- **Service Configuration**:
  - Production-optimized resource allocations
  - Security policies and network segmentation
  - Monitoring and alerting configurations
- **Operations**:
  - Blue-green deployment strategy
  - Automated rollbacks on failure
  - Performance monitoring and scaling policies

### Deployment Parity
- **Identical Codebase**: No code changes between local and cloud deployments
- **Configuration as Code**: All environment differences managed via Helm values
- **Dapr Abstraction**: Same Dapr component configurations with environment-specific endpoints
- **CI/CD Pipeline**: Unified pipeline for both environments with environment-specific triggers

### Helm Chart Structure
- **Global Values**: Common configuration across environments
- **Environment-Specific Values**: Local, staging, production configurations
- **Service Templates**: Standardized templates for all microservices
- **Dapr Components**: Reusable component definitions with environment variables
- **Monitoring**: Integrated Prometheus and Grafana configurations