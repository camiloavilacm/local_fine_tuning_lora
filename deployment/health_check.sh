#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

PORT=${1:-7860}
TIMEOUT=${2:-5}

echo "Health check on port $PORT..."

if curl -s --max-time $TIMEOUT "http://localhost:$PORT" > /dev/null 2>&1; then
    echo "✓ Server is healthy"
    exit 0
else
    echo "✗ Server is not responding"
    exit 1
fi