import importlib.util
import subprocess
import ollama
import sys

# Mapping for packages where pip name differs from import name
PACKAGE_TO_IMPORT_MAP = {
    "SQLAlchemy": "sqlalchemy",
    "beautifulsoup4": "bs4",
    "Pillow": "PIL",
    "python-dotenv": "dotenv"
}

def check_dependencies():
    """Checks if all packages from requirements.txt are installed and returns a list of missing ones."""
    print("Checking for required dependencies...")
    missing_packages = []
    try:
        with open('requirements.txt', 'r') as f:
            for line in f:
                package = line.strip()
                package_name = package.split('==')[0]
                import_name = PACKAGE_TO_IMPORT_MAP.get(package_name, package_name)
                if package and not importlib.util.find_spec(import_name):
                    missing_packages.append(package)
    except FileNotFoundError:
        print("Error: requirements.txt not found.")
        return False

    if not missing_packages:
        print("All dependencies are installed.")
    return missing_packages

def check_ollama_service():
    """Checks if the Ollama service is running and prompts the user to start it if not."""
    print("Checking for Ollama service...")
    try:
        # The list() command is a lightweight way to check the connection
        ollama.list()
        print("Ollama service is running.")
        return True
    except ollama.ResponseError as e:
        if 'ollama is not running' in str(e):
            print("\nOllama service is not running.")
            print("Please start the Ollama service by running the following command in a separate terminal:")
            print("\n    ollama serve\n")
            print("Once the service is running, please restart this application.")
            sys.exit(1)
        else:
            print(f"An unexpected error occurred with Ollama: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to connect to Ollama. Ensure Ollama is installed and configured correctly. Error: {e}")
        sys.exit(1)
