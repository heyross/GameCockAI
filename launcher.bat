@echo off
REM This batch file launches and manages the Gamecock application.

:start
REM Run the main Python script.
python main.py

REM Check the exit code. If it's 10, a restart is requested.
if %errorlevel% == 10 (
    echo.
    echo Dependencies installed. Restarting application...
    timeout /t 1 /nobreak > nul
    goto start
)

echo.
echo Application exited.
pause
