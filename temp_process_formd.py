import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from processor import process_formd_data
from config import FORMD_SOURCE_DIR

if __name__ == "__main__":
    print("Processing Form D data...")
    process_formd_data(FORMD_SOURCE_DIR)
    print("Processing complete.")
