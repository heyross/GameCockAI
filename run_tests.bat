@echo off
REM GameCock AI Vector Embeddings Test Runner for Windows
echo 🧪 GameCock AI Vector Embeddings Test Suite
echo ==========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "tests\run_all_tests.py" (
    echo ❌ Test runner not found. Please run this from the GameCock root directory.
    pause
    exit /b 1
)

REM Parse command line arguments
set SKIP_PERFORMANCE=
set SKIP_INTEGRATION=
set VERBOSE=

:parse_args
if "%1"=="" goto run_tests
if "%1"=="--skip-performance" set SKIP_PERFORMANCE=--skip-performance
if "%1"=="--skip-integration" set SKIP_INTEGRATION=--skip-integration
if "%1"=="--verbose" set VERBOSE=--verbose
if "%1"=="-v" set VERBOSE=--verbose
shift
goto parse_args

:run_tests
echo 🚀 Starting test suite...
echo.

REM Run the tests
python tests\run_all_tests.py %SKIP_PERFORMANCE% %SKIP_INTEGRATION% %VERBOSE%

REM Check exit code
if errorlevel 1 (
    echo.
    echo ❌ Tests failed. See output above for details.
    pause
    exit /b 1
) else (
    echo.
    echo ✅ All tests passed successfully!
    echo 📁 Results saved to test_results\ directory
    pause
    exit /b 0
)
