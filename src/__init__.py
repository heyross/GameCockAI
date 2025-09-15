"""
GameCock AI Source Package
Proper Python package structure for portable imports
"""

import sys
import os
from pathlib import Path

# Get the absolute path to the GameCockAI directory (parent of src)
_package_dir = Path(__file__).parent
_gamecock_dir = _package_dir.parent

# Add GameCockAI directory to sys.path if not already there
if str(_gamecock_dir) not in sys.path:
    sys.path.insert(0, str(_gamecock_dir))

# This ensures that all src modules can import from the parent directory
# using relative imports that resolve correctly