@echo off
setlocal
echo ===================================================
echo     NY TAGGING SYSTEM V2 - STARTUP (DEV MODE)
echo ===================================================
echo.

:: 1. Start Print Agent
echo [1/3] Starting Print Agent (Port 1234)...
start "NY-Print-Agent" cmd /k "cd client_agent && uv run print_agent.py"

:: 2. Start Backend V2
echo [2/3] Starting Backend V2 (Port 8000)...
start "NY-Backend-V2" cmd /k "cd backend_v2 && uv run main.py"

:: 3. Wait a bit for services to initialize
timeout /t 5 /nobreak >nul

:: 4. Start Frontend V2
echo [3/3] Starting Frontend V2 (Port 5173)...
start "NY-Frontend-V2" cmd /k "cd frontend_v2 && npm run dev"

echo.
echo ===================================================
echo  SERVICES LAUNCHED!
echo  - Print Agent: Port 1234
echo  - Backend: http://127.0.0.1:8000/api/v1/health
echo  - Frontend: http://127.0.0.1:5173
echo ===================================================
pause
