#!/bin/sh
set -e

echo "=== Starting Placement Portal Application ==="

# Check if Redis URL is configured
if [ -n "$REDIS_URL" ] || [ -n "$CELERY_BROKER_URL" ]; then
    echo "Starting Celery Worker in background..."
    celery -A app.celery worker --loglevel=info --concurrency=2 &
    WORKER_PID=$!

    echo "Starting Celery Beat Scheduler in background..."
    celery -A app.celery beat --loglevel=info &
    BEAT_PID=$!
else
    echo "Notice: REDIS_URL not provided. Celery worker/beat skipped."
fi

# Trap termination signals to gracefully shutdown background jobs
cleanup() {
    echo "Caught shutdown signal. Stopping Celery processes..."
    if [ -n "$WORKER_PID" ]; then kill -TERM "$WORKER_PID" 2>/dev/null || true; fi
    if [ -n "$BEAT_PID" ]; then kill -TERM "$BEAT_PID" 2>/dev/null || true; fi
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "Starting Gunicorn Web Server..."
PORT="${PORT:-5000}"
exec gunicorn --chdir backend "app:create_app()" \
    --bind "0.0.0.0:${PORT}" \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
