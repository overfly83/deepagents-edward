@echo off
echo Starting Weather Assistant Backend Server...
echo.

cd /d %~dp0
echo Running backend server...
echo Application URL: http://localhost:8000
echo To stop the service, press Ctrl+C.
echo.

.venv\Scripts\python.exe -m uvicorn src.agents.server:app --reload --host 0.0.0.0 --port 8000 --log-level info