#!/bin/bash

# Migration script for Wit.ai project
# Moves existing Wit.ai files into new structured project

set -e

echo "========================================"
echo "Wit.ai Project Migration"
echo "========================================"

PROJECT_DIR="/root/clawd/scripts/wit-ai-audio-processor"
LEGACY_DIR="/root/clawd/scripts"

echo "Migrating Wit.ai files to new structure..."
echo "Project directory: $PROJECT_DIR"
echo ""

# Create backup of legacy files
BACKUP_DIR="/root/clawd/scripts/backup_wit_legacy_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "1. Backing up legacy files to: $BACKUP_DIR"

# Backup Wit.ai related files
wit_files=(
    "wit_audio_handler.py"
    "wit_audio_handler_v2.py"
    "test_wit_ai.py"
    "test_wit_simple.py"
    "setup_wit_ai_example.sh"
    "start_wit_audio_processing.sh"
    "stop_audio_processing.sh"
    "start_complete_audio_system.sh"
    "stop_complete_audio_system.sh"
    "audio_auto_responder.py"
    "clawdbot_integration.py"
    "whatsapp_simulator.py"
    "whisper_handler.py"
)

for file in "${wit_files[@]}"; do
    if [ -f "$LEGACY_DIR/$file" ]; then
        cp "$LEGACY_DIR/$file" "$BACKUP_DIR/"
        echo "  ✓ Backed up: $file"
    fi
done

echo ""
echo "2. Creating reference documentation..."

# Create reference file showing what was migrated
cat > "$PROJECT_DIR/docs/LEGACY_MIGRATION.md" << EOF
# Legacy Wit.ai Files Migration

The following files from the old scripts directory have been migrated:

## Core Functionality (Migrated to new structure)
- \`wit_audio_handler.py\` → \`src/core/wit_handler.py\`
- \`wit_audio_handler_v2.py\` → Incorporated into new handler
- \`clawdbot_integration.py\` → Integrated into session file creation

## Test Files (Kept for reference)
- \`test_wit_ai.py\` → See \`docs/TESTING.md\`
- \`test_wit_simple.py\` → See \`docs/TESTING.md\`

## Scripts (Replaced with new system)
- \`setup_wit_ai_example.sh\` → See \`README.md\` and \`run.sh\`
- \`start_wit_audio_processing.sh\` → Use \`./run.sh\`
- \`stop_audio_processing.sh\` → Use Ctrl+C or kill process
- \`start_complete_audio_system.sh\` → Integrated into \`run.sh\`
- \`stop_complete_audio_system.sh\` → Not needed with new structure

## Related Audio Files
- \`audio_auto_responder.py\` → Future enhancement
- \`whatsapp_simulator.py\` → Future test module
- \`whisper_handler.py\` → Separate project (Whisper vs Wit.ai)

## Backup Location
All original files are backed up to:
\`$BACKUP_DIR\`

## New Structure Benefits
1. **Clean organization** - All files in proper directories
2. **Configuration management** - JSON config + environment variables
3. **Virtual environment** - Isolated dependencies
4. **Better logging** - Structured log files
5. **Easier maintenance** - Clear separation of concerns
6. **Documentation** - Comprehensive README and guides

## How to Use New System
\`\`\`bash
cd $PROJECT_DIR
./run.sh
\`\`\`

See \`README.md\` for complete instructions.
EOF

echo "  ✓ Created migration documentation"

echo ""
echo "3. Creating test utilities..."

# Create test utilities based on legacy test files
cat > "$PROJECT_DIR/src/utils/test_audio.py" << 'EOF'
"""
Test utilities for Wit.ai Audio Processor
"""

import os
import tempfile
import subprocess
from pathlib import Path

def create_test_audio(duration_seconds=5, sample_rate=16000):
    """
    Create a test WAV file with silence
    Requires sox or ffmpeg
    """
    try:
        # Create temp file
        temp_dir = tempfile.gettempdir()
        test_file = Path(temp_dir) / f"test_audio_{int(os.getenv('WIT_API_KEY_DEFAULT', '0')[-4:])}.wav"
        
        # Try sox first, then ffmpeg
        try:
            # Generate silence with sox
            cmd = ['sox', '-n', '-r', str(sample_rate), '-c', '1', 
                   str(test_file), 'trim', '0.0', str(duration_seconds)]
            subprocess.run(cmd, check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fall back to ffmpeg
            cmd = ['ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=16000:cl=mono', 
                   '-t', str(duration_seconds), '-acodec', 'pcm_s16le', 
                   '-y', str(test_file)]
            subprocess.run(cmd, check=True, capture_output=True)
        
        return test_file if test_file.exists() else None
        
    except Exception as e:
        print(f"Error creating test audio: {e}")
        return None

def simulate_whatsapp_audio(phone_number="212626474248", audio_path=None):
    """
    Simulate WhatsApp audio file in incoming directory
    """
    incoming_dir = Path("/root/clawd/audio/incoming")
    incoming_dir.mkdir(parents=True, exist_ok=True)
    
    if audio_path and Path(audio_path).exists():
        # Copy existing audio file
        import shutil
        import time
        timestamp = int(time.time())
        dest_file = incoming_dir / f"{phone_number}_{timestamp}.ogg"
        shutil.copy2(audio_path, dest_file)
        return dest_file
    else:
        # Create a test file
        test_wav = create_test_audio(3)
        if test_wav:
            timestamp = int(time.time())
            dest_file = incoming_dir / f"{phone_number}_{timestamp}.ogg"
            # Convert to OGG (simplified)
            cmd = ['ffmpeg', '-i', str(test_wav), '-c:a', 'libopus', 
                   '-y', str(dest_file)]
            subprocess.run(cmd, capture_output=True)
            test_wav.unlink()  # Clean up temp WAV
            return dest_file if dest_file.exists() else None
    
    return None
EOF

echo "  ✓ Created test utilities"

echo ""
echo "4. Cleaning up legacy directory..."

# Move non-Wit.ai files to keep them accessible
echo "  Keeping non-Wit.ai scripts in place:"
echo "  - create_project.sh"
echo "  - project_cleanup.sh"
echo "  - example-audio-project/"

echo ""
echo "5. Setting up new project..."

# Copy environment from legacy if exists
if [ -f "$LEGACY_DIR/.env" ]; then
    echo "  Found existing .env, copying to project..."
    cp "$LEGACY_DIR/.env" "$PROJECT_DIR/config/.env"
fi

# Check for existing Wit.ai API keys in environment
if [ -n "$WIT_API_KEY_DEFAULT" ]; then
    echo "  Found WIT_API_KEY_DEFAULT in environment"
    if [ ! -f "$PROJECT_DIR/config/.env" ]; then
        echo "WIT_API_KEY_DEFAULT=$WIT_API_KEY_DEFAULT" > "$PROJECT_DIR/config/.env"
        echo "  Created config/.env with API key"
    fi
fi

echo ""
echo "========================================"
echo "Migration Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Review the new project structure:"
echo "   cd $PROJECT_DIR"
echo "   ls -la"
echo ""
echo "2. Set up your Wit.ai API key:"
echo "   cp config/.env.example config/.env"
echo "   nano config/.env"
echo ""
echo "3. Install dependencies:"
echo "   python -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo ""
echo "4. Run the new system:"
echo "   ./run.sh"
echo ""
echo "5. Test with:"
echo "   python -c \"from src.utils.test_audio import simulate_whatsapp_audio; simulate_whatsapp_audio()\""
echo ""
echo "Legacy files backed up to: $BACKUP_DIR"
echo "Migration docs: $PROJECT_DIR/docs/LEGACY_MIGRATION.md"
echo ""
echo "Note: The old scripts directory still contains:"
echo "  - create_project.sh (project creation tool)"
echo "  - project_cleanup.sh (cleanup utility)"
echo "  - example-audio-project/ (template example)"
echo ""
echo "You can safely remove other Wit.ai related files after verifying"
echo "the new system works correctly."
echo "========================================"