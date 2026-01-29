"""
Utility functions for example-audio-project
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
