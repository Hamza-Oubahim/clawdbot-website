# Project Structure Guide

## For Each New Project:

1. **Create a new folder** inside `/root/clawd/scripts/` with a descriptive name
2. **Include only essential files** (remove tests, logs, temporary files)
3. **Always run under appropriate environment** (virtual env, node env, etc.)
4. **Maintain clean structure** with clear organization

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

- Remove `__pycache__/`, `node_modules/`, `.git/` (unless it's the main repo)
- Remove test files unless they're essential examples
- Remove log files, temporary files, and build artifacts
- Keep only production-ready or core demonstration code

## Environment Setup:

- Python: Always use virtual environment (`venv/` in project root)
- Node.js: Use project-local `node_modules/`
- Shell: Set proper environment variables in `run.sh`
