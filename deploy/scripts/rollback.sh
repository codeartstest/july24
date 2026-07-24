#!/bin/bash
set -euo pipefail

echo "=== Rollback Todo List ==="

cd /opt/todo-list

echo "[1/3] Getting previous commit..."
PREVIOUS_COMMIT=$(git rev-parse HEAD~1 2>/dev/null || echo "")

if [ -z "$PREVIOUS_COMMIT" ]; then
    echo "No previous commit found. Cannot rollback."
    exit 1
fi

echo "Rolling back to: $(git rev-parse --short $PREVIOUS_COMMIT)"

echo "[2/3] Checking out previous commit..."
git checkout "$PREVIOUS_COMMIT"

echo "[3/3] Rebuilding and restarting..."
docker compose build --no-cache
docker compose up -d

echo ""
echo "Rollback complete. Current version: $(git rev-parse --short HEAD)"
echo "Frontend: http://localhost"
echo "Backend:  http://localhost:8000"