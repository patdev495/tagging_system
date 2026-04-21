@echo off
setlocal

echo ========================================
echo   BACKEND EXE BUILDER (Directory Mode)
echo ========================================

:: Clean previous build artifacts
if exist build rd /s /q build
if exist dist rd /s /q dist

echo.
echo [1/3] Installing Build Dependencies...
:: Using uv for fast installation if available, fallback to pip
where uv >nul 2>nul
if %errorlevel% equ 0 (
    uv pip install pyinstaller
) else (
    pip install pyinstaller
)

echo.
echo [2/3] Running PyInstaller...
:: --onedir: Create a folder with .exe and _internal
:: --name: Output executable name
:: --collect-all: Ensure all sub-dependencies of these critical libs are included
uv run pyinstaller --noconfirm --onedir --console --name "NY_Tagging_Backend" ^
    --collect-all fastapi ^
    --collect-all uvicorn ^
    --collect-all pydantic ^
    --collect-all sqlalchemy ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [!] Build failed! Please check the errors above.
    pause
    exit /b %errorlevel%
)

echo.
echo [3/3] Finalizing...
:: Copy .env template or existing .env if safe (optional)
if exist .env (
    echo Copying .env to build folder...
    copy .env dist\NY_Tagging_Backend\ >nul
)

echo.
echo ========================================
echo   BUILD SUCCESSFUL!
echo ========================================
echo  Location: backend\dist\NY_Tagging_Backend\
echo  To run: Double click NY_Tagging_Backend.exe
echo.
echo  NOTE: Remember to place your 'frontend/dist' 
echo  folder next to the 'NY_Tagging_Backend.exe'.
echo ========================================

pause
