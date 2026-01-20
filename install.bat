@echo off

echo ========================================
echo DeepAgents Demo - Installation Script
echo ========================================

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo Error: Python not found! Please install Python and add it to PATH.
    pause
    exit /b 1
)

echo.
echo Setting up project directory...
cd /d "%~dp0"

echo.
echo Checking for existing virtual environment...
if exist ".venv" (
    echo WARNING: Virtual environment already exists!
    echo Press Enter to delete and reinstall, or Ctrl+C to cancel.
    pause
    rmdir /s /q ".venv"
)

echo.
echo Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment!
    pause
    exit /b 1
)

echo.
echo Activating virtual environment and installing dependencies...
call ".venv\Scripts\activate.bat" && pip install --upgrade pip && pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Error: Installation failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo To run the backend server:
echo   .venv\Scripts\python -m uvicorn backend.server:app --reload

echo To run the weather agent directly:
echo   .venv\Scripts\python -m src.deepagents_demo.agents.weather_agent

pause