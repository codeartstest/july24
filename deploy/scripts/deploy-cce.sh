#!/bin/bash
set -euo pipefail

K8S_DIR="$(cd "$(dirname "$0")/.." && pwd)/k8s"
CREDENTIALS_DIR="${HOME}/.kube"

echo "=== Todo List CCE Deployment ==="
echo ""

echo "[1/5] Fetching CCE cluster credentials..."
if [ ! -f "$CREDENTIALS_DIR/config" ]; then
    echo "ERROR: No kubeconfig found at $CREDENTIALS_DIR/config"
    echo "Run: huaweicloud cce kubectl configure --cluster-id <CLUSTER_ID>"
    exit 1
fi
echo "Kubeconfig found."

echo ""
echo "[2/5] Building Docker images on worker node..."
docker build -t todo-backend:latest ../../backend
docker build -t todo-frontend:latest ../../frontend

echo ""
echo "[3/5] Loading images into CCE (local build — no registry)..."
echo "NOTE: For multi-node, push to SWR (Huawei Container Registry) instead."
kind load docker-image todo-backend:latest 2>/dev/null || \
    echo "  (Not using kind — images available on local Docker daemon)"

echo ""
echo "[4/5] Applying Kubernetes manifests..."
kubectl apply -f "$K8S_DIR/backend-pvc.yaml"
kubectl apply -f "$K8S_DIR/backend-deployment.yaml"
kubectl apply -f "$K8S_DIR/backend-service.yaml"
kubectl apply -f "$K8S_DIR/frontend-deployment.yaml"
kubectl apply -f "$K8S_DIR/frontend-service.yaml"
kubectl apply -f "$K8S_DIR/ingress.yaml"

echo ""
echo "[5/5] Waiting for rollout..."
kubectl rollout status deployment/todo-backend --timeout=120s
kubectl rollout status deployment/todo-frontend --timeout=120s

echo ""
echo "=== CCE Deployment Complete ==="
echo ""
echo "Pods:"
kubectl get pods -l app
echo ""
echo "Services:"
kubectl get svc
echo ""
echo "Ingress:"
kubectl get ingress
echo ""
echo "Access the app via the Ingress external IP above."