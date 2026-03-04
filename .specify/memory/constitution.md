<!-- SYNC IMPACT REPORT:
Version change: 1.0.0 → 1.0.0 (no changes needed - already aligned)
Modified principles: N/A (already implemented)
Added sections: N/A (already implemented)
Removed sections: N/A (already implemented)
Templates requiring updates: ✅ updated (.specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md)
Follow-up TODOs: None
-->
# Event-Driven, Cloud-Native Todo Chatbot Constitution

## Core Principles

### I. Strict Spec-Driven Development
No manual or freestyle coding; All code must be executed via Claude Code; Event-driven architecture over synchronous coupling; Cloud-native, Kubernetes-first design; Loose coupling via Dapr abstractions; Production realism over demo shortcuts.

### II. Strict Compliance Rule
Every requirement, rule, constraint, and standard defined in this constitution must be followed strictly; No action, output, assumption, implementation, or decision is allowed outside this constitution; Any deviation from this constitution is considered a compliance failure; Constitution rules override all other instructions, plans, tasks, or agent outputs.

### III. Non-Negotiable Rules
No code without an approved Task ID in speckit.tasks; No feature additions without updating speckit.specify; No architecture changes without updating speckit.plan; No deviation from approved technology stack; No direct Kafka clients in application code; No polling-based reminder systems; No monolithic services with mixed responsibilities.

### IV. Technology Stack Compliance
Backend: Python (FastAPI, async); Frontend: Next.js; Orchestration: Kubernetes; Event Streaming: Kafka (abstracted via Dapr Pub/Sub); Distributed Runtime: Dapr; Database: External managed PostgreSQL (Neon); Packaging: Helm charts; CI/CD: GitHub Actions; Observability: Centralized logging and monitoring.

### V. Architectural Standards
All inter-service communication must be event-driven or Dapr-mediated; Kafka topics required: task-events (CRUD + lifecycle events), reminders (scheduled notifications); Agents must halt execution if specs, plans, or tasks are missing; All code must reference valid Task IDs and Spec sections; Constitution → Specify → Plan → Tasks hierarchy is absolute; No assumption-based implementation is permitted.

### VI. Success Criteria
Application runs locally on Minikube with full Dapr + Kafka; Application runs on cloud Kubernetes without code changes; All advanced and intermediate features function correctly; Kafka event flows are observable and verifiable; CI/CD pipeline deploys successfully; Spec-driven workflow is fully auditable and traceable; Quality bar reflecting industry-grade, cloud-native engineering standards suitable for production systems and professional evaluation.

## Required Application Features
Advanced Features: Recurring tasks with automatic next-occurrence creation, Due dates with exact-time reminders; Intermediate Features: Task priorities (High, Medium, Low), Tags and categorization, Search functionality, Filter and sort operations. All features must be validated end-to-end via event-driven flows.

## Development Workflow
Core Development Principles: Strict Spec-Driven Development (Specify → Plan → Tasks → Implement); Architectural Standards: Event-driven architecture, Cloud-native design, Loose coupling. All implementations must be validated end-to-end via event-driven flows.

## Governance
Amendment procedure follows semantic versioning (MAJOR/MINOR/PATCH); Compliance review required for all implementations; Constitution supersedes all other practices; All implementations must reference valid Task IDs and Spec sections; Strict adherence to the approved technology stack; Agentic execution via Claude Code + SpecKitPlus via MCP.

**Version**: 1.0.0 | **Ratified**: 2026-01-16 | **Last Amended**: 2026-01-16