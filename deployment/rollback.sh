#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

ENVIRONMENT=${1:-staging}

echo "=========================================="
echo "  Rollback: $ENVIRONMENT"
echo "=========================================="

echo "[1/3] Stopping current server..."
pkill -f chat_ui_flask 2>/dev/null || true
sleep 2

echo "[2/3] Checking for previous version..."
PREVIOUS_LOG="logs/${ENVIRONMENT}.log.previous"
if [ -f "$PREVIOUS_LOG" ]; then
    echo "Found previous log: $PREVIOUS_LOG"
fi

echo "[3/3] Starting fresh server..."
cd "$PROJECT_DIR"
LOG_FILE="logs/${ENVIRONMENT}.log"

PYTHONPATH="$PROJECT_DIR:$PROJECT_DIR/scripts" nohup python3 "$PROJECT_DIR/scripts/chat_ui_flask.py" > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

sleep 10

if kill -0 $SERVER_PID 2>/dev/null; then
    echo ""
    echo "=========================================="
    echo "  ✓ Rollback complete"
    echo "  PID: $SERVER_PID"
    echo "=========================================="
else
    echo "Error: Server failed to start after rollback"
    exit 1
fi