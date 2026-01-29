#!/bin/bash
# init_project.sh - Automate sandboxed project creation

PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: ./init_project.sh <project_name>"
    exit 1
fi

PROJECT_DIR="/Users/bs/Desktop/GitHub/clawdbot-website/scripts/$PROJECT_NAME"

echo "🚀 Initializing sandboxed project: $PROJECT_NAME..."

# Create structure
mkdir -p "$PROJECT_DIR"/{src,config,docs}
touch "$PROJECT_DIR"/requirements.txt

# Setup Python Sandbox (venv)
echo "🐍 Creating virtual environment..."
python3 -m venv "$PROJECT_DIR/venv"

# Create run.sh template
cat <<EOF > "$PROJECT_DIR/run.sh"
#!/bin/bash
# Auto-generated entry point for $PROJECT_NAME

# Activate sandbox
source \$(dirname "\$0")/venv/bin/activate

# Run main script
python3 \$(dirname "\$0")/src/main.py "\$@"
EOF

chmod +x "$PROJECT_DIR/run.sh"

# Create main.py template
cat <<EOF > "$PROJECT_DIR/src/main.py"
import sys

def main():
    print(f"Project '$PROJECT_NAME' is active in its sandbox.")

if __name__ == "__main__":
    main()
EOF

echo "✅ Project $PROJECT_NAME initialized at $PROJECT_DIR"
echo "💡 To run: $PROJECT_DIR/run.sh"
