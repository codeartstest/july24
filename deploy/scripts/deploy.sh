#!/bin/bash
set -euo pipefail

DEPLOY_DIR="/opt/todo-list"
REPO_URL="https://github.com/codeartstest/july24.git"
BRANCH="main"
COMMIT_SHA="${1:-$(git ls-remote "$REPO_URL" "refs/heads/$BRANCH" | awk '{print $1}')}"

echo "=== Todo List Deployment ==="
echo "Target commit: $COMMIT_SHA"
echo "Deploy dir:    $DEPLOY_DIR"
echo ""

echo "[1/6] Installing Docker if not present..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
    echo "Docker installed."
else
    echo "Docker already installed."
fi

echo ""
echo "[2/6] Cloning repository..."
if [ -d "$DEPLOY_DIR/.git" ]; then
    cd "$DEPLOY_DIR"
    git fetch origin
    git checkout "$BRANCH"
    git reset --hard "origin/$BRANCH"
else
    git clone -b "$BRANCH" "$REPO_URL" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi
echo "Checked out: $(git rev-parse --short HEAD)"

echo ""
echo "[3/6] Building Docker images..."
docker compose build --no-cache

echo ""
echo "[4/6] Stopping existing containers..."
docker compose down --remove-orphans 2>/dev/null || true

echo ""
echo "[5/6] Starting containers..."
docker compose up -d

echo ""
echo "[6/6] Health check..."
MAX_RETRIES=30
RETRY_COUNT=0
HEALTH_URL="http://localhost:8000/health"

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        echo "Health check PASSED: $HEALTH_URL"
        echo ""
        echo "=== Deployment Successful ==="
        echo "Frontend: http://localhost"
        echo "Backend:  http://localhost:8000"
        echo "API docs: http://localhost:8000/docs"
        exit 0
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

echo "Health check FAILED after $MAX_RETRIES retries."
echo "Checking container logs..."
docker compose logs --tail=50
exit 1