"# Event-Driven, Cloud-Native Todo Chatbot

A sophisticated todo management system built with event-driven architecture, featuring recurring tasks, exact-time reminders, and advanced search capabilities.

## Features

- **Event-Driven Architecture**: Built on Dapr and Kafka for scalable, resilient messaging
- **Recurring Tasks**: Automatic generation of future task instances based on patterns
- **Exact-Time Reminders**: Precise scheduling using Dapr Jobs API
- **Advanced Search & Filtering**: Full-text search, filtering, and sorting capabilities
- **Real User Accounts**: Persistent identity with profile management
- **Cloud-Native**: Kubernetes-first design with local Minikube and cloud deployment options

## Architecture

The system consists of multiple microservices that communicate through Dapr's building blocks:

- **Task Management Service**: Core task CRUD operations
- **Recurring Task Service**: Pattern processing and instance generation
- **Reminder Service**: Scheduled notifications via Dapr Jobs API
- **Search Service**: Full-text search and filtering
- **Chat Interface Service**: Natural language command processing
- **User Management Service**: Authentication and profile management
- **Frontend Service**: Next.js-based user interface

## Technologies

- **Backend**: Python (FastAPI)
- **Frontend**: Next.js
- **Orchestration**: Kubernetes
- **Event Streaming**: Kafka (via Dapr Pub/Sub)
- **Distributed Runtime**: Dapr
- **Database**: PostgreSQL (via Dapr State Management)
- **Packaging**: Helm charts

## Local Development

### Prerequisites

- Docker Desktop (with Kubernetes enabled) or Minikube
- kubectl
- Helm 3+
- Dapr CLI
- Python 3.9+
- Node.js 16+

### Setup

1. Initialize Dapr:
   ```bash
   dapr init -k
   dapr status -k
   ```

2. Start local Kafka cluster:
   ```bash
   kubectl create -f https://strimzi.io/install/latest?namespace=kafka
   kubectl create -f https://strimzi.io/examples/latest/kafka/kafka-ephemeral-single.yaml -n kafka
   kubectl wait kafka/my-cluster --for=condition=Ready --timeout=300s -n kafka
   ```

3. Deploy application components:
   ```bash
   helm install todo-chatbot ./charts/todo-chatbot \
     --set global.environment=local \
     --set postgresql.enabled=true \
     --set kafka.connection=kafka-kafka-brokers.kafka.svc.cluster.local:9092
   ```

4. Configure Dapr components (see quickstart guide for details)

## Deployment

The application supports both local (Minikube) and cloud (AKS/GKE/OKE) deployments with identical configuration structures.

## Contributing

See the development guidelines in the specification documents." 
