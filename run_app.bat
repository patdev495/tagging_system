@echo off
setlocal
set PORT=8000

echo ========================================
echo       NY TAGGING SYSTEM LAUNCHER
echo ========================================
echo.

:: 1. Check for Production Build first
set BUILD_EXE=backend\dist\NY_Tagging_Backend\NY_Tagging_Backend.exe
if exist "%BUILD_EXE%" (
    echo [FOUND] Production build detected.
    echo Launching executable...
    start "" "%BUILD_EXE%"
    goto end
)

:: 2. Fallback to Python Script
echo [INFO] Production build not found. Running via Python...
echo Checking for Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.12+ or build the .exe first.
    pause
    exit /b
)

echo Starting Backend on port %PORT%...
cd backend
python main.py

:end
echo.
echo System started. Use Ctrl+C to stop the Python process if needed.
pause
