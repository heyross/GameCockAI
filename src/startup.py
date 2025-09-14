import importlib.util
import subprocess
import ollama
import sys

# Mapping for packages where pip name differs from import name
PACKAGE_TO_IMPORT_MAP = {
    "SQLAlchemy": "sqlalchemy",
    "beautifulsoup4": "bs4",
    "Pillow": "PIL",
    "python-dotenv": "dotenv",
    "sentence-transformers": "sentence_transformers",
    "faiss-cpu": "faiss",
    "faiss-gpu": "faiss",
    "scikit-learn": "sklearn",
    "asyncio-mqtt": "asyncio_mqtt"
}

def check_dependencies():
    """Checks if all packages from requirements.txt are installed and installs missing ones."""
    print("Checking for required dependencies...")
    missing_packages = []
    
    try:
        with open('requirements.txt', 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Extract package name (handle version specifiers like >=, ==, etc.)
                package_name = line.split('>=')[0].split('==')[0].split('<=')[0].split('!=')[0].split('~=')[0].strip()
                
                # Get the import name 
                import_name = PACKAGE_TO_IMPORT_MAP.get(package_name, package_name.lower().replace('-', '_'))
                
                # Check if package is installed
                if not importlib.util.find_spec(import_name):
                    missing_packages.append(line)  # Keep the full line with version
                    
    except FileNotFoundError:
        print("Error: requirements.txt not found.")
        return False

    if missing_packages:
        print(f"Found {len(missing_packages)} missing dependencies:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        
        print("\nInstalling missing dependencies...")
        return install_missing_packages(missing_packages)
    else:
        print("All dependencies are installed.")
        return True

def install_missing_packages(packages):
    """Install missing packages using pip."""
    try:
        for package in packages:
            print(f"Installing {package}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Successfully installed {package}")
            
        print("✅ All missing dependencies have been installed.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        print(f"Error output: {e.stderr}")
        print("\nPlease install the dependencies manually:")
        print(f"pip install {' '.join(packages)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during installation: {e}")
        return False

def check_cuda_support():
    """Checks CUDA availability and provides installation guidance if needed."""
    print("Checking CUDA support...")
    
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        cuda_version = torch.version.cuda if hasattr(torch, 'version') else None
        device_count = torch.cuda.device_count()
        
        if cuda_available:
            print(f"✅ CUDA is available!")
            print(f"   CUDA version: {cuda_version}")
            print(f"   GPU devices: {device_count}")
            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                print(f"   Device {i}: {device_name}")
            return True
        else:
            print("⚠️  CUDA is not available")
            print("   This will limit performance but the application will still work on CPU")
            
            # Check if PyTorch is CPU-only version
            if '+cpu' in torch.__version__:
                print("\n🔧 CUDA Setup Required:")
                print("   You have the CPU-only version of PyTorch installed.")
                print("   To enable CUDA acceleration:")
                print("   1. Install CUDA toolkit from: https://developer.nvidia.com/cuda-downloads")
                print("   2. Reinstall PyTorch with CUDA support:")
                print("      pip uninstall torch torchvision torchaudio")
                print("      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
                print("   3. Restart the application")
            else:
                print("\n🔧 CUDA Setup Required:")
                print("   PyTorch supports CUDA but CUDA is not properly installed.")
                print("   1. Install NVIDIA GPU drivers")
                print("   2. Install CUDA toolkit from: https://developer.nvidia.com/cuda-downloads")
                print("   3. Restart the application")
            
            print("\n💡 The application will continue with CPU-only processing.")
            return False
            
    except ImportError:
        print("❌ PyTorch not available - cannot check CUDA support")
        return False
    except Exception as e:
        print(f"⚠️  Error checking CUDA support: {e}")
        return False

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
