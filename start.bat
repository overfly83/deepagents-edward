@echo off
set DEBUG_MODE=false

REM Check if debug parameter is provided
if "%1"=="debug" (
    set DEBUG_MODE=true
    echo Debug mode enabled...
)

echo Starting Weather Assistant Web Application...
echo.

REM Check if frontend static files already exist
set STATIC_DIR=%~dp0src\agents\static
if exist "%STATIC_DIR%\index.html" (
    echo Frontend static files already exist, skipping build...
) else (
    echo Compiling frontend code...
    echo Please wait, this may take some time...
    cd /d %~dp0frontend
    call npm run build

    if %ERRORLEVEL% neq 0 (
        echo.
        echo Error: Frontend compilation failed!
        echo Please check the frontend code for errors and try again.
        echo.
        pause
        exit /b %ERRORLEVEL%
    )

    echo.
    echo Frontend compilation successful!
)

echo.
echo Starting backend server...
echo Application URL: http://localhost:8000
echo To stop the service, press Ctrl+C.
echo.

cd /d %~dp0
set PYTHONPATH=%~dp0src;%PYTHONPATH%
if "%DEBUG_MODE%"=="true" (
    .venv\Scripts\python.exe -m uvicorn src.agents.server:app --reload --host 0.0.0.0 --port 8000 --log-level debug
) else (
    .venv\Scripts\python.exe -m uvicorn src.agents.server:app --reload --host 0.0.0.0 --port 8000 --log-level info
)