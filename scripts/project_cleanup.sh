#!/bin/bash

# Project Cleanup Script
# Removes unnecessary files and maintains clean project structure

set -e

PROJECT_DIR="$1"

if [ -z "$PROJECT_DIR" ]; then
    echo "Usage: $0 <project-directory>"
    echo "Example: $0 /root/clawd/scripts/my-project"
    exit 1
fi

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Directory $PROJECT_DIR does not exist"
    exit 1
fi

echo "Cleaning up project: $PROJECT_DIR"

# Remove common unnecessary directories
echo "Removing cache and build directories..."
find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -type d -name "build" -exec rm -rf {} + 2>/dev/null || true

# Remove common unnecessary files
echo "Removing temporary and log files..."
find "$PROJECT_DIR" -type f -name "*.log" -delete 2>/dev/null || true
find "$PROJECT_DIR" -type f -name "*.tmp" -delete 2>/dev/null || true
find "$PROJECT_DIR" -type f -name "*.temp" -delete 2>/dev/null || true
find "$PROJECT_DIR" -type f -name ".DS_Store" -delete 2>/dev/null || true
find "$PROJECT_DIR" -type f -name "Thumbs.db" -delete 2>/dev/null || true

# Remove test files (optional - keep if they're important examples)
# Uncomment if you want to remove test files:
# echo "Removing test files..."
# find "$PROJECT_DIR" -type f -name "*test*.py" -delete 2>/dev/null || true
# find "$PROJECT_DIR" -type f -name "*spec*.js" -delete 2>/dev/null || true
# find "$PROJECT_DIR" -type f -name "*test*.js" -delete 2>/dev/null || true

echo "Cleanup complete!"
echo ""
echo "Recommended structure for $PROJECT_DIR:"
echo "  project-name/"
echo "  ├── src/                    # Source code"
echo "  ├── config/                 # Configuration"
echo "  ├── docs/                   # Documentation"
echo "  ├── requirements.txt        # Dependencies"
echo "  └── run.sh                  # Launch script"
