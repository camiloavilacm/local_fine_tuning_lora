#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

ENVIRONMENT=${1:-staging}
BRANCH=${2:-develop}

echo "=========================================="
echo "  Deployment: $ENVIRONMENT"
echo "  Branch: $BRANCH"
echo "=========================================="

if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo "Error: Environment must be 'staging' or 'production'"
    exit 1
fi

CONFIG_DIR="$SCRIPT_DIR/$ENVIRONMENT/config.yaml"

if [ ! -f "$CONFIG_DIR" ]; then
    echo "Error: Config file not found: $CONFIG_DIR"
    exit 1
fi

echo ""
echo "[1/5] Checking environment..."
cd "$PROJECT_DIR"

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

if ! python3 -c "import mlx_lm" 2>/dev/null; then
    echo "Warning: mlx_lm not installed"
fi

echo "[2/5] Checking adapter exists..."
ADAPTER_PATH=$(grep "adapter_path:" "$CONFIG_DIR" | cut -d':' -f2 | tr -d ' ')
if [ ! -d "$ADAPTER_PATH" ]; then
    echo "Error: Adapter not found: $ADAPTER_PATH"
    exit 1
fi

echo "[3/5] Checking knowledge file..."
KNOWLEDGE_FILE=$(grep "knowledge_file:" "$CONFIG_DIR" | cut -d':' -f2- | tr -d ' ')
if [ ! -f "$KNOWLEDGE_FILE" ]; then
    echo "Error: Knowledge file not found: $KNOWLEDGE_FILE"
    exit 1
fi

echo "[4/5] Killing existing server..."
pkill -f chat_ui_flask 2>/dev/null || true
sleep 2

echo "[5/5] Starting server for $ENVIRONMENT..."
LOG_FILE="logs/${ENVIRONMENT}.log"
mkdir -p "$PROJECT_DIR/logs"

PYTHONPATH="$PROJECT_DIR:$PROJECT_DIR/scripts" nohup python3 "$PROJECT_DIR/scripts/chat_ui_flask.py" > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

sleep 10

if kill -0 $SERVER_PID 2>/dev/null; then
    echo ""
    echo "=========================================="
    echo "  ✓ Deployment successful!"
    echo "  Environment: $ENVIRONMENT"
    echo "  PID: $SERVER_PID"
    echo "  Log: $LOG_FILE"
    echo "=========================================="
    
    if curl -s -f http://localhost:7860 > /dev/null 2>&1; then
        echo "  Status: Server responding"
    else
        echo "  Warning: Server not responding yet"
    fi
else
    echo "Error: Server failed to start"
    exit 1
fi