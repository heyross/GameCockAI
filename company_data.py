import json
import os

TARGETS_FILE = "targets.json"

def load_target_companies():
    """Loads the target companies list from a JSON file."""
    if os.path.exists(TARGETS_FILE):
        with open(TARGETS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_target_companies(targets):
    """Saves the target companies list to a JSON file."""
    with open(TARGETS_FILE, 'w') as f:
        json.dump(targets, f, indent=4)

# Load target companies on startup
TARGET_COMPANIES = load_target_companies()
