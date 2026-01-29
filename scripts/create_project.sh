#!/bin/bash

# Project Creation Script
# Creates a new well-structured project folder

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <project-name>"
    echo "Example: $0 audio-processor"
    exit 1
fi

PROJECT_NAME="$1"
PROJECT_DIR="/root/clawd/scripts/$PROJECT_NAME"

if [ -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory $PROJECT_DIR already exists"
    exit 1
fi

echo "Creating new project: $PROJECT_NAME"
echo "Location: $PROJECT_DIR"

# Create directory structure
mkdir -p "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR/src"
mkdir -p "$PROJECT_DIR/config"
mkdir -p "$PROJECT_DIR/docs"
mkdir -p "$PROJECT_DIR/data"  # For data files if needed
mkdir -p "$PROJECT_DIR/logs"  # For log files (gitignored)

# Create basic files
cat > "$PROJECT_DIR/README.md" << EOF
# $PROJECT_NAME

## Description
Brief description of the project.

## Setup
\`\`\`bash
# Create virtual environment (Python)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or for Node.js
npm install
\`\`\`

## Usage
\`\`\`bash
./run.sh
\`\`\`

## Structure
- \`src/\` - Source code
- \`config/\` - Configuration files
- \`docs/\` - Documentation
- \`data/\` - Data files
- \`logs/\` - Log files (gitignored)
EOF

# Create Python virtual environment
echo "Creating Python virtual environment..."
python -m venv "$PROJECT_DIR/venv" 2>/dev/null || echo "Note: Python venv creation skipped (python3-venv may not be installed)"

# Create requirements.txt
cat > "$PROJECT_DIR/requirements.txt" << EOF
# Project dependencies
# Add your Python dependencies here
EOF

# Create run.sh
cat > "$PROJECT_DIR/run.sh" << 'EOF'
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
EOF

chmod +x "$PROJECT_DIR/run.sh"

# Create .gitignore
cat > "$PROJECT_DIR/.gitignore" << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env
.venv

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
logs/
data/temp/
*.log
EOF

# Create config template
cat > "$PROJECT_DIR/config/settings.json" << EOF
{
  "project_name": "$PROJECT_NAME",
  "version": "1.0.0",
  "description": "Project configuration",
  "settings": {
    "debug": false,
    "log_level": "INFO"
  }
}
EOF

# Create env template
cat > "$PROJECT_DIR/config/.env.example" << EOF
# Environment variables template
# Copy to .env and fill in actual values

PROJECT_NAME=$PROJECT_NAME
DEBUG=false
LOG_LEVEL=INFO

# API Keys (if needed)
# API_KEY=your_api_key_here
# DATABASE_URL=your_database_url_here
EOF

# Create main Python file
cat > "$PROJECT_DIR/src/main.py" << EOF
#!/usr/bin/env python3
"""
Main entry point for $PROJECT_NAME
"""

import os
import sys
import json
import logging
from pathlib import Path

def setup_logging():
    """Configure logging"""
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def load_config():
    """Load configuration from config/settings.json"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    """Main function"""
    logger = setup_logging()
    config = load_config()
    
    logger.info(f"Starting {config['project_name']} v{config['version']}")
    logger.info(f"Description: {config['description']}")
    
    # Your main logic here
    logger.info("Project is running!")
    
    # Example: Process something
    logger.info("Processing complete")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF

# Create a simple utility module
cat > "$PROJECT_DIR/src/utils.py" << EOF
"""
Utility functions for $PROJECT_NAME
"""

import os
import json
from pathlib import Path

def read_json_file(filepath):
    """Read and parse a JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def write_json_file(filepath, data):
    """Write data to a JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def ensure_directory(path):
    """Ensure a directory exists"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path
EOF

echo ""
echo "Project created successfully!"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_DIR"
echo "2. Review and update config files in config/"
echo "3. Add dependencies to requirements.txt"
echo "4. Run: ./run.sh"
echo ""
echo "To clean up unnecessary files later:"
echo "./project_cleanup.sh $PROJECT_DIR"
