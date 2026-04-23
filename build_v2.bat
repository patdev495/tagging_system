@echo off
echo ===================================================
echo    NY TAGGING SYSTEM V3 - PRODUCTION BUILDER
echo ===================================================
echo.

:: 1. Build Frontend
echo [1/3] Building Frontend V2...
cd frontend_v2
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed!
    pause
    exit /b
)
cd ..

:: 2. Build Backend
echo [2/3] Building Backend V2 EXE...
cd backend_v2
uv run pyinstaller --noconfirm --onedir --console --name "NY_Tagging_System" ^
    --add-data "src;src" ^
    --hidden-import pyodbc ^
    main.py
if %errorlevel% neq 0 (
    echo [ERROR] Backend build failed!
    pause
    exit /b
)
cd ..

:: 3. Finalize
echo [3/3] Finalizing build...
if not exist "release" mkdir release
xcopy /E /I /Y "backend_v2\dist\NY_Tagging_System" "release\NY_Tagging_System"
xcopy /E /I /Y "frontend_v2\dist" "release\frontend_v2\dist"
copy "backend_v2\.env" "release\NY_Tagging_System\.env"

echo.
echo ===================================================
echo  BUILD COMPLETE!
echo  Check the "release" folder for your deployment files.
echo ===================================================
pause
