@echo off
setlocal enabledelayedexpansion

echo Creating GamecockAI Windows Installer...
echo ====================================

:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.7 or higher first.
    pause
    exit /b 1
)

:: Check if pip is installed
where pip >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo pip is not installed. Please ensure pip is installed and in PATH.
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv "%CD%\venv"
call "%CD%\venv\Scripts\activate.bat"

:: Install required packages
echo Installing required packages...
pip install --upgrade pip
pip install pyinstaller
pip install -r "%CD%\..\requirements.txt"

:: Create the executable
echo Creating executable...
pyinstaller --onefile --windowed --name GamecockAI --icon=..\assets\icon.ico ..\main.py

:: Create the MSI installer
echo Creating MSI installer...
pip install pyinstaller-versionfile
python -m PyInstaller --onefile --windowed --name GamecockAI --icon=..\assets\icon.ico --version-file=version.txt ..\main.py

:: Create a simple launcher script
echo Creating launcher...
echo @echo off > "%CD%\GamecockAI_Launcher.bat"
echo cd /d "%~dp0" >> "%CD%\GamecockAI_Launcher.bat"
echo start "" "%CD%\dist\GamecockAI.exe" >> "%CD%\GamecockAI_Launcher.bat"

echo.
echo ====================================
echo Installation package created successfully!
echo 1. Find the executable in: %CD%\dist\GamecockAI.exe
echo 2. Use GamecockAI_Launcher.bat to run the application
echo 3. The MSI installer is available in: %CD%\dist\
echo ====================================
pause
