#!/bin/bash
set -euo pipefail

K8S_DIR="$(cd "$(dirname "$0")/.." && pwd)/k8s"

echo "=== Rollback CCE Deployment ==="

echo "[1/2] Rolling back deployments..."
kubectl rollout undo deployment/todo-backend
kubectl rollout undo deployment/todo-frontend

echo "[2/2] Waiting for rollback to complete..."
kubectl rollout status deployment/todo-backend --timeout=120s
kubectl rollout status deployment/todo-frontend --timeout=120s

echo ""
echo "Rollback complete."
kubectl get pods -l app