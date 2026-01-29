# Project Structure Guide

## For Each New Project:

1. **Unique Identity:** Every project MUST have a descriptive folder name in `scripts/`.
2. **Mandatory Sandboxing:** EVERY Python project MUST use a project-local `venv/`. No exceptions.
3. **Clean On-Boarding:** Include a `run.sh` that handles environment activation and execution.
4. **Simplicity First:** Keep structure flat. Remove any file not actively used in production.
5. **Rollback Readiness:** Every major folder in `scripts/` should be tracked or have a backup strategy. No project should be irrecoverable.

## Folder Structure Template:

```
/root/clawd/scripts/project-name/
├── src/                    # Source code
│   ├── main.py            # Main entry point
│   ├── utils/             # Utility functions
│   └── modules/           # Modular components
├── config/                # Configuration files
│   ├── settings.json      # Main settings
│   └── env.example        # Environment template
├── docs/                  # Documentation
│   └── README.md         # Project documentation
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
└── run.sh                # Launch script
```

## Cleanup Rules:

- **Token Wash:** Remove all comments or documentation that do not add functional value. Concise code > verbose comments for token efficiency.
- Remove `__pycache__/`, `node_modules/`, `.git/` (unless it's the main repo)
- Remove test files unless they're essential examples
- Remove log files, temporary files, and build artifacts
- Keep only production-ready or core demonstration code

## Environment Setup:

- **Python:** Mandatory virtual environment (`python3 -m venv venv`). Always use `./venv/bin/python` or source the environment.
- **Node.js:** Use `npm init -y` and project-local `node_modules/`.
- **Shell:** Each project must have a `run.sh` entry point that guarantees the correct environment is loaded.
- **Cleanup:** All projects must be isolated. No project should write to the workspace root.
