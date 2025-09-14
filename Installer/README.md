# GamecockAI Windows Installer

This directory contains the necessary files to create a Windows installer for GamecockAI.

## Prerequisites

- Windows 7 or later
- Python 3.7 or higher (64-bit recommended)
- pip (Python package manager)
- Administrator privileges (for installation)
- nVidia GPU with 8GB of vRAM, 3xxx or later version
- Plenty of disk storage and at least 32gb of RAM

## Creating the Installer

1. Open a Command Prompt as Administrator
2. Navigate to this directory:
   ```
   cd path\to\GameCockAI\Installer
   ```
3. Run the installer script:
   ```
   create_installer.bat
   ```
4. Follow the on-screen instructions

## What the Installer Does

1. Creates a virtual environment
2. Installs all required Python packages
3. Creates a standalone executable using PyInstaller
4. Generates a Windows MSI installer
5. Creates a launcher script

## Output Files

After successful execution, you'll find:
- `dist/GamecockAI.exe` - The standalone executable
- `dist/GamecockAI.msi` - The Windows installer package
- `GamecockAI_Launcher.bat` - A launcher script for easy startup

## Installation Options

### Option 1: Using the MSI Installer (Recommended for End Users)
1. Double-click `GamecockAI.msi`
2. Follow the installation wizard
3. Launch from the Start Menu or desktop shortcut

### Option 2: Using the Standalone Executable
1. Copy the `dist` folder to the target machine
2. Run `GamecockAI.exe` directly

### Option 3: Using the Launcher Script
1. Copy `GamecockAI_Launcher.bat` and the `dist` folder to the target machine
2. Run `GamecockAI_Launcher.bat`

## Troubleshooting

- If you get a "Python not found" error, ensure Python is installed and added to PATH
- For missing DLL errors, install the latest [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- If the application crashes on startup, run it from Command Prompt to see error messages

## Customization

- To change the application icon, replace `../assets/icon.ico`
- Update version information in `version.txt`
- Modify the installer script (`create_installer.bat`) for additional customizations

## License

This installer is part of GamecockAI and is distributed under the same license terms.
