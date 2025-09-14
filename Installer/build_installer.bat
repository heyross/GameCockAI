@echo off
setlocal enabledelayedexpansion

echo Building GamecockAI Installer...
echo ====================================

:: Check if NSIS is installed
where makensis >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo NSIS (Nullsoft Scriptable Install System) is not installed or not in PATH.
    echo Please download and install NSIS from: https://nsis.sourceforge.io/Download
    pause
    exit /b 1
)

:: Check if we're running as admin
net session >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Running with administrator privileges.
) else (
    echo This script requires administrator privileges to create proper shortcuts.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

:: Create build directory if it doesn't exist
if not exist "build" mkdir build

:: Copy required files to build directory
echo Copying files...
xcopy /E /I /Y "..\*.*" "build\"

:: Build the installer
echo Building installer...
makensis /V2 /DINSTALLER_VERSION=1.0.0 "GamecockAI_Installer.nsi"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ====================================
    echo Installer created successfully!
    echo Location: %CD%\GamecockAI_Setup_1.0.0.exe
    echo ====================================
) else (
    echo.
    echo ====================================
    echo Error building installer. Check the output above for details.
    echo ====================================
    pause
    exit /b 1
)

:: Clean up (optional)
rem rmdir /S /Q build

echo Done!
pause
