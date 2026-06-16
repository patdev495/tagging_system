@echo off
echo ===================================================
echo    NY TAGGING SYSTEM V3 - PRODUCTION BUILDER
echo ===================================================
echo.

:: 1. Build Frontend
echo [1/4] Building Frontend V2...
cd frontend_v2
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed!
    pause
    exit /b
)
cd ..

:: 2. Build Backend
echo [2/4] Building Backend V2 EXE...
cd backend_v2
uv run pyinstaller --noconfirm --onedir --console --name "NY_Tagging_System" ^
    --add-data "src;src" ^
    --collect-all pydantic ^
    --collect-all pydantic_core ^
    --collect-submodules pydantic_core ^
    --hidden-import pydantic_core ^
    --hidden-import pydantic_core._pydantic_core ^
    --hidden-import pyodbc ^
    --hidden-import win32com ^
    --hidden-import win32com.client ^
    --hidden-import pythoncom ^
    --hidden-import win32gui ^
    --hidden-import win32con ^
    --hidden-import win32print ^
    --hidden-import PIL ^
    main.py
if %errorlevel% neq 0 (
    echo [ERROR] Backend build failed!
    pause
    exit /b
)
cd ..

:: 3. Build Print Agent
echo [3/4] Building Print Agent V2 EXE...
cd print_agent_v2
uv run pyinstaller --noconfirm --onefile --console --name "NY_Print_Agent" ^
    --hidden-import win32com ^
    --hidden-import win32com.client ^
    --hidden-import pythoncom ^
    agent.py
if %errorlevel% neq 0 (
    echo [ERROR] Print Agent build failed!
    pause
    exit /b
)
cd ..

:: 4. Finalize
echo [4/4] Finalizing build...
if not exist "release" mkdir release
if exist "release\NY_Tagging_System" rmdir /S /Q "release\NY_Tagging_System"
xcopy /E /I /Y "backend_v2\dist\NY_Tagging_System" "release\NY_Tagging_System"
xcopy /E /I /Y "frontend_v2\dist" "release\NY_Tagging_System\static"
copy /Y "print_agent_v2\dist\NY_Print_Agent.exe" "release\NY_Print_Agent.exe"
xcopy /E /I /Y "backend_v2\resources" "release\NY_Tagging_System\resources"
copy "backend_v2\.env" "release\NY_Tagging_System\.env"

echo.
echo ===================================================
echo  BUILD COMPLETE!
echo  Check the "release" folder for your deployment files.
echo ===================================================
pause
