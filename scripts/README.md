# Scripts Directory - Project Organization

## Structure Implemented

From now on, each new project should be created as a separate folder inside `/root/clawd/scripts/` with the following structure:

```
project-name/
├── src/                    # Source code
├── config/                 # Configuration files
├── docs/                   # Documentation
├── data/                   # Data files (optional)
├── logs/                   # Log files (gitignored)
├── venv/                   # Python virtual environment
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── run.sh                 # Launch script (runs under env)
└── .gitignore            # Git ignore rules
```

## Tools Available

### 1. Create New Project
```bash
./create_project.sh <project-name>
```
Creates a new well-structured project folder with all necessary files.

### 2. Cleanup Existing Project
```bash
./project_cleanup.sh <project-directory>
```
Removes unnecessary files (cache, logs, temp files) from a project.

### 3. Project Structure Guide
See `/root/clawd/PROJECT_STRUCTURE_GUIDE.md` for detailed guidelines.

## Example Workflow

1. **Create a new project:**
   ```bash
   cd /root/clawd/scripts
   ./create_project.sh my-audio-tool
   ```

2. **Navigate to project:**
   ```bash
   cd my-audio-tool
   ```

3. **Set up environment:**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Run the project:**
   ```bash
   ./run.sh
   ```

5. **Clean up when done:**
   ```bash
   cd /root/clawd/scripts
   ./project_cleanup.sh my-audio-tool
   ```

## Current Scripts (to be organized)

The following scripts in the root of this directory should be moved into appropriate project folders:

- Audio processing scripts → `audio-processor/` project
- WhatsApp integration scripts → `whatsapp-bot/` project  
- Wit.ai scripts → `wit-ai-integration/` project
- Test scripts → Remove or move to test projects

## Rules to Follow

1. **One project per folder** - No mixing of unrelated scripts
2. **Clean structure** - Remove tests, logs, cache files
3. **Environment isolation** - Always use virtual env/container
4. **Documentation** - Each project must have README.md
5. **Entry point** - Each project must have a `run.sh` or equivalent
