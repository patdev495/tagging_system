@echo off
setlocal
echo ===================================================
echo     NY TAGGING SYSTEM V2 - STARTUP (DEV MODE)
echo ===================================================
echo.

:: 1. Start Backend V2 (includes BarTender Engine)
echo [1/2] Starting Backend V2 (Port 8001, BarTender integrated)...
start "NY-Backend-V2" cmd /k "cd backend_v2 && uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

:: 2. Wait for backend to initialize
ping 127.0.0.1 -n 6 >nul

:: 3. Start Frontend V2
echo [2/2] Starting Frontend V2 (Port 5173)...
start "NY-Frontend-V2" cmd /k "cd frontend_v2 && npm run dev -- --host"

echo.
echo ===================================================
echo  SERVICES LAUNCHED!
echo  - Backend + BarTender: http://127.0.0.1:8001
echo  - Frontend: http://127.0.0.1:5173
echo  - Print Agent: REMOVED (integrated into Backend)
echo ===================================================
pause
