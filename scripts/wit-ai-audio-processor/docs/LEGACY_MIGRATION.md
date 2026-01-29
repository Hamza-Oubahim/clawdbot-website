# Legacy Wit.ai Files Migration

The following files from the old scripts directory have been migrated:

## Core Functionality (Migrated to new structure)
- `wit_audio_handler.py` → `src/core/wit_handler.py`
- `wit_audio_handler_v2.py` → Incorporated into new handler
- `clawdbot_integration.py` → Integrated into session file creation

## Test Files (Kept for reference)
- `test_wit_ai.py` → See `docs/TESTING.md`
- `test_wit_simple.py` → See `docs/TESTING.md`

## Scripts (Replaced with new system)
- `setup_wit_ai_example.sh` → See `README.md` and `run.sh`
- `start_wit_audio_processing.sh` → Use `./run.sh`
- `stop_audio_processing.sh` → Use Ctrl+C or kill process
- `start_complete_audio_system.sh` → Integrated into `run.sh`
- `stop_complete_audio_system.sh` → Not needed with new structure

## Related Audio Files
- `audio_auto_responder.py` → Future enhancement
- `whatsapp_simulator.py` → Future test module
- `whisper_handler.py` → Separate project (Whisper vs Wit.ai)

## Backup Location
All original files are backed up to:
`/root/clawd/scripts/backup_wit_legacy_20260129_044140`

## New Structure Benefits
1. **Clean organization** - All files in proper directories
2. **Configuration management** - JSON config + environment variables
3. **Virtual environment** - Isolated dependencies
4. **Better logging** - Structured log files
5. **Easier maintenance** - Clear separation of concerns
6. **Documentation** - Comprehensive README and guides

## How to Use New System
```bash
cd /root/clawd/scripts/wit-ai-audio-processor
./run.sh
```

See `README.md` for complete instructions.
