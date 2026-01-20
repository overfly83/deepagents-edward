@echo off
echo Stopping Weather Assistant Web Application...
echo.

echo Looking for and stopping backend server...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo table /nh ^| find "server.py"') do (
    echo Stopping Python process, PID: %%i
    taskkill /pid %%i /f
)

echo.
echo Looking for and stopping frontend server...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq node.exe" /fo table /nh ^| find "vite"') do (
    echo Stopping Node process, PID: %%i
    taskkill /pid %%i /f
)

echo.
echo All services have been stopped!
echo.
pause