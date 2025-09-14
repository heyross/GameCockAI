import importlib.util
import subprocess
import ollama
import sys
import re
import os
import sys
import platform
import requests
from typing import List, Tuple
from pathlib import Path

# Mapping for packages where pip name differs from import name
PACKAGE_TO_IMPORT_MAP = {
    "SQLAlchemy": "sqlalchemy",
    "beautifulsoup4": "bs4",
    "Pillow": "PIL",
    "python-dotenv": "dotenv",
    "sentence-transformers": "sentence_transformers",
    "scikit-learn": "sklearn"
}

def is_windows() -> bool:
    """Check if the current platform is Windows."""
    return platform.system() == 'Windows'

def get_pip_command() -> List[str]:
    """Get the correct pip command based on the current Python environment."""
    # Use the same Python executable that's running this script
    python_executable = sys.executable
    if not python_executable:
        return ["pip"]
    return [python_executable, "-m", "pip"]

def install_packages(packages: List[str]) -> Tuple[bool, str]:
    """Install the specified packages using pip."""
    if not packages:
        return True, "No packages to install."
    
    pip_cmd = get_pip_command()
    cmd = pip_cmd + ["install", "--upgrade"] + packages
    
    try:
        print(f"Installing packages: {', '.join(packages)}")
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to install packages. Error: {e.stderr}"
        print(error_msg)
        return False, error_msg

def check_dependencies() -> Tuple[bool, List[str]]:
    """
    Check if all packages from requirements.txt are installed.
    
    Returns:
        Tuple[bool, List[str]]: (success, missing_packages)
            - success: True if all dependencies are satisfied or installed successfully
            - missing_packages: List of packages that couldn't be installed
    """
    print("\n=== Checking Dependencies ===")
    missing_packages = []
    requirements_path = Path('requirements.txt')
    
    if not requirements_path.exists():
        print("⚠️  requirements.txt not found. Cannot verify dependencies.")
        return False, []
    
    # Read requirements
    with open(requirements_path, 'r') as f:
        required_packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Check which packages are missing
    for package in required_packages:
        package_name = re.split(r'[<>=!~]=?', package)[0].strip()
        import_name = PACKAGE_TO_IMPORT_MAP.get(package_name, package_name)
        
        # Special handling for packages with different import names
        try:
            if not importlib.util.find_spec(import_name):
                missing_packages.append(package)
        except (ImportError, ModuleNotFoundError):
            missing_packages.append(package)
    
    if not missing_packages:
        print("✅ All dependencies are installed.")
        return True, []
    
    print(f"\n⚠️  Missing {len(missing_packages)} package(s):")
    for pkg in missing_packages:
        print(f"  - {pkg}")
    
    return False, missing_packages

def check_ollama_service():
    """Checks if the Ollama service is running and prompts the user to start it if not."""
    print("Checking for Ollama service...")
    try:
        # The list() command is a lightweight way to check the connection
        ollama.list()
        print("Ollama service is running.")
        return True
    except (ollama.ResponseError, requests.exceptions.ConnectionError) as e:
        print("\n--- Ollama Service Not Found ---")
        print("Could not connect to the Ollama service.")
        print("Please ensure the Ollama application is running on your machine.")
        print("If it is not running, you can start it with the following command in a separate terminal:")
        print("\n    ollama serve\n")
        input("Press Enter to exit.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while checking for Ollama: {e}")
        sys.exit(1)
