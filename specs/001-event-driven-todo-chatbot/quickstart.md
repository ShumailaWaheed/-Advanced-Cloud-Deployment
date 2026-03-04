# Quickstart Guide: Event-Driven, Cloud-Native Todo Chatbot

**Date**: 2026-01-16
**Feature**: Event-Driven, Cloud-Native Todo Chatbot
**Branch**: 001-event-driven-todo-chatbot

## Overview

This guide provides a quick introduction to setting up and running the event-driven, cloud-native todo chatbot locally using Minikube. This environment mirrors the cloud deployment architecture and allows for rapid development and testing.

## Prerequisites

- Docker Desktop (with Kubernetes enabled) or Minikube
- kubectl
- Helm 3+
- Dapr CLI
- Python 3.9+
- Node.js 16+ (for frontend development)

## Local Development Setup

### 1. Initialize Dapr

```bash
# Install Dapr into your local Kubernetes cluster
dapr init -k

# Verify installation
dapr status -k
```

### 2. Start Local Kafka Cluster

```bash
# Install Strimzi Kafka operator
kubectl create -f https://strimzi.io/install/latest?namespace=kafka
kubectl create -f https://strimzi.io/examples/latest/kafka/kafka-ephemeral-single.yaml -n kafka

# Wait for Kafka to be ready
kubectl wait kafka/my-cluster --for=condition=Ready --timeout=300s -n kafka
```

### 3. Deploy Application Components

```bash
# Navigate to the project directory
cd advanced-claude-deployment

# Install the Helm chart for local development
helm install todo-chatbot ./charts/todo-chatbot \
  --set global.environment=local \
  --set postgresql.enabled=true \
  --set kafka.connection=kafka-kafka-brokers.kafka.svc.cluster.local:9092
```

### 4. Configure Dapr Components

Create the necessary Dapr component files:

**pubsub.yaml** (for Kafka integration):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-kafka-brokers.kafka.svc.cluster.local:9092"
  - name: consumerGroup
    value: "todo-chatbot-group"
  - name: clientID
    value: "todo-chatbot"
  - name: authRequired
    value: "false"
```

**statestore.yaml** (for PostgreSQL):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "host=postgresql.default.svc.cluster.local user=postgres password=example dbname=todochatbot port=5432 sslmode=disable"
  - name: table
    value: "state"
  - name: actorStateStore
    value: "true"
```

Apply these components:
```bash
kubectl apply -f pubsub.yaml
kubectl apply -f statestore.yaml
```

### 5. Access the Application

```bash
# Port forward to access the services
kubectl port-forward svc/todo-chatbot-api 8000:80

# Access the frontend
kubectl port-forward svc/todo-chatbot-frontend 3000:80
```

## Development Workflow

### Service Development

1. **Task Management Service** (`services/task-management/`)
   - Python FastAPI service
   - Handles task CRUD operations
   - Publishes events via Dapr pub/sub

2. **Recurring Task Service** (`services/recurring-task/`)
   - Processes recurring task patterns
   - Generates new task instances
   - Uses Dapr Jobs API for scheduling

3. **Reminder Service** (`services/reminder/`)
   - Manages reminder scheduling
   - Sends notifications at specified times
   - Integrates with Dapr Jobs API

4. **Chat Interface Service** (`services/chat-interface/`)
   - Processes natural language commands
   - Translates to task operations
   - Provides chat responses

### Running Services Locally

For local development, you can run services individually:

```bash
# Set up Dapr with your service
dapr run --app-id task-service --app-port 8001 --dapr-http-port 3501 python app.py

# Call the service through Dapr
curl -X POST http://localhost:3501/v1.0/invoke/task-service/method/create-task \
  -H "Content-Type: application/json" \
  -d '{"title": "Sample Task", "userId": "123"}'
```

## Testing

### Unit Tests
```bash
# Run unit tests for Python services
cd services/task-management
python -m pytest tests/unit/

# Run frontend tests
cd services/frontend
npm test
```

### Integration Tests
```bash
# Run integration tests with Dapr
dapr run --app-id test-runner -- python -m pytest tests/integration/
```

### End-to-End Tests
```bash
# Run E2E tests that simulate user flows
npm run test:e2e
```

## Configuration

### Environment Variables

The application uses the following environment variables:

**Task Management Service:**
- `APP_PORT`: Port for the service (default: 8001)
- `DAPR_HTTP_PORT`: Dapr HTTP port (default: 3500)
- `DAPR_GRPC_PORT`: Dapr gRPC port (default: 50001)

**Database Configuration:**
- `POSTGRES_HOST`: PostgreSQL host
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

## Troubleshooting

### Common Issues

1. **Dapr Sidecar Not Starting**
   - Ensure Dapr is installed in Kubernetes: `dapr status -k`
   - Check pod logs: `kubectl logs <pod-name> -c daprd`

2. **Kafka Connection Issues**
   - Verify Kafka cluster is running: `kubectl get kafka -n kafka`
   - Check Kafka logs: `kubectl logs -l strimzi.io/name=my-cluster-kafka -n kafka`

3. **Service Communication Problems**
   - Verify Dapr components are configured: `kubectl get components.dapr.io`
   - Check service endpoints: `kubectl get endpoints`

### Useful Commands

```bash
# Check all pods
kubectl get pods

# Check Dapr sidecars
kubectl get pods -l app.kubernetes.io/part-of=dapr

# View application logs
kubectl logs -l app=todo-chatbot

# Describe a specific pod for troubleshooting
kubectl describe pod <pod-name>
```

## Next Steps

1. Review the [Implementation Plan](./plan.md) for detailed architecture
2. Examine the [Data Model](./data-model.md) for entity relationships
3. Look at the [API Contracts](./contracts/) for service interfaces
4. Explore the [Research Summary](./research.md) for technical decisions