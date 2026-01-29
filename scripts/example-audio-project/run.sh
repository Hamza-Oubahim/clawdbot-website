#!/bin/bash

# Project Runner Script
# Always runs under appropriate environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate Python virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating Python virtual environment..."
    source venv/bin/activate
fi

# Load environment variables if config exists
if [ -f "config/.env" ]; then
    echo "Loading environment variables..."
    set -a
    source config/.env
    set +a
fi

# Run the main script
echo "Starting $PROJECT_NAME..."
python src/main.py "$@"
