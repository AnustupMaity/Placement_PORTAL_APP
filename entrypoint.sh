#!/bin/bash
set -e

echo "=== Starting Placement Portal Application ==="

# Set Celery working directory to backend
BACKEND_DIR="/app/backend"

# Check if Redis URL is configured
if [ -n "$REDIS_URL" ] || [ -n "$CELERY_BROKER_URL" ]; then
    echo "Starting Celery Worker with embedded Beat Scheduler in background..."
    celery -A app.celery --workdir "$BACKEND_DIR" worker --pool=solo -B --loglevel=info &
    WORKER_PID=$!
else
    echo "Notice: REDIS_URL not provided. Celery worker/beat skipped."
fi

# Trap termination signals (INT TERM) for graceful container shutdown
cleanup() {
    echo "Caught shutdown signal. Stopping Celery processes..."
    if [ -n "$WORKER_PID" ]; then kill "$WORKER_PID" 2>/dev/null || true; fi
    exit 0
}
trap cleanup INT TERM

echo "Starting Gunicorn Web Server on port ${PORT:-5000}..."
PORT="${PORT:-5000}"
exec gunicorn --chdir "$BACKEND_DIR" "app:create_app()" \
    --bind "0.0.0.0:${PORT}" \
    --workers 1 \
    --worker-class eventlet \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
