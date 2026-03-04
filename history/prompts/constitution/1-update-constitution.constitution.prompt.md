---
id: 1
title: Update Constitution
stage: constitution
date: 2026-01-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.constitution
labels: [constitution,update,spec-driven-development]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```text
/sp.constitution

Project: Event-Driven, Cloud-Native Todo Chatbot
Phase: Phase V – Advanced Cloud Deployment

Purpose:
This project implements a production-grade, event-driven Todo Chatbot using
Spec-Driven Development (SDD). The objective is to demonstrate advanced cloud-native
architecture, Kubernetes deployment, Kafka-based event streaming, and Dapr-powered
distributed runtime using an agentic development workflow.

────────────────────────────────────────
CORE DEVELOPMENT PRINCIPLES
────────────────────────────────────────
- Strict Spec-Driven Development (Specify → Plan → Tasks → Implement)
- No manual or freestyle coding
- All code must be executed via Claude Code
- Event-driven architecture over synchronous coupling
- Cloud-native, Kubernetes-first design
- Loose coupling via Dapr abstractions
- Production realism over demo shortcuts

────────────────────────────────────────
STRICT COMPLIANCE RULE (NON-OVERRIDABLE)
────────────────────────────────────────
- Every requirement, rule, constraint, and standard defined in this constitution
  must be followed strictly.
- No action, output, assumption, implementation, or decision is allowed outside
  this constitution.
- Any deviation from this constitution is considered a compliance failure.
- Constitution rules override all other instructions, plans, tasks, or agent outputs.

────────────────────────────────────────
NON-NEGOTIABLE RULES
────────────────────────────────────────
- No code without an approved Task ID in speckit.tasks
- No feature additions without updating speckit.specify
- No architecture changes without updating speckit.plan
- No deviation from approved technology stack
- No direct Kafka clients in application code
- No polling-based reminder systems
- No monolithic services with mixed responsibilities

────────────────────────────────────────
REQUIRED APPLICATION FEATURES
────────────────────────────────────────
Advanced Features:
- Recurring tasks with automatic next-occurrence creation
- Due dates with exact-time reminders

Intermediate Features:
- Task priorities (High, Medium, Low)
- Tags and categorization
- Search functionality
- Filter and sort operations

All features must be validated end-to-end via event-driven flows.

────────────────────────────────────────
APPROVED TECHNOLOGY STACK
────────────────────────────────────────
- Backend: Python (FastAPI, async)
- Frontend: Next.js
- Orchestration: Kubernetes
  - Local: Minikube
  - Cloud: AKS / GKE / Oracle OKE
- Event Streaming: Kafka (abstracted via Dapr Pub/Sub)
- Distributed Runtime: Dapr
  - Pub/Sub
  - State Management
  - Jobs API (required)
  - Bindings / Cron (optional fallback only if approved)
  - Secrets Management
  - Service Invocation
- Database: External managed PostgreSQL (Neon)
- Packaging: Helm charts (reused and extended from Phase IV)
- CI/CD: GitHub Actions
- Observability: Centralized logging and monitoring
- Agentic Execution: Claude Code + SpecKitPlus via MCP

────────────────────────────────────────
ARCHITECTURAL STANDARDS
────────────────────────────────────────
- All inter-service communication must be event-driven or Dapr-mediated
- Kafka topics required:
  - task-events (CRUD + lifecycle events)
  - reminders (scheduled notifications)
- Agents must halt execution if specs, plans, or tasks are missing
- All code must reference valid Task IDs and Spec sections
- Constitution → Specify → Plan → Tasks hierarchy is absolute
- No assumption-based implementation is permitted

────────────────────────────────────────
SUCCESS CRITERIA
────────────────────────────────────────
- Application runs locally on Minikube with full Dapr + Kafka
- Application runs on cloud Kubernetes without code changes
- All advanced and intermediate features function correctly
- Kafka event flows are observable and verifiable
- CI/CD pipeline deploys successfully
- Spec-driven workflow is fully auditable and traceable

Quality Bar:
This project must reflect industry-grade, cloud-native engineering standards
suitable for production systems and professional evaluation.
```

## Response snapshot

Updated the project constitution file (.specify/memory/constitution.md) based on the provided user input, incorporating all the specified principles, requirements, and standards for the Event-Driven, Cloud-Native Todo Chatbot project. The constitution now includes:

- Core principles for spec-driven development
- Strict compliance rules
- Non-negotiable implementation rules
- Technology stack compliance requirements
- Architectural standards
- Success criteria
- Required application features
- Development workflow guidelines
- Governance procedures

The constitution is versioned as 1.0.0 and dated 2026-01-16.

## Outcome

- ✅ Impact: Created/updated constitution file with comprehensive project governance
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md
- 🔁 Next prompts: Proceed with project planning and specification
- 🧠 Reflection: Constitution provides clear governance framework for the project

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin project specification based on constitution