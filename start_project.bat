@echo off
REM ============================================
REM Gram Meter Project - Structured Startup
REM ============================================
REM Starts:
REM 1. Django Backend (8000)
REM 2. Frontend App (5173)
REM 3. Virtual Meter Feed (Admin console/virtual_meter_gov.py)
REM ============================================

title Gram Meter Project
color 0A

echo.
echo ============================================
echo    Gram Meter Project Startup
echo ============================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if not exist "logs" mkdir logs
if not exist ".pids" mkdir .pids

echo [1/6] Cleaning old listeners on 8000, 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /PID %%a /F 2>nul
timeout /t 2 /nobreak >nul

echo [2/6] Preparing Python environment...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    python -m venv .venv
    call .venv\Scripts\activate.bat
)
pip install -q -r backend\requirements.txt

echo [3/6] Ensuring frontend dependencies...
if not exist "frontend\node_modules" (
    cd /d "%SCRIPT_DIR%frontend"
    call npm install
    cd /d "%SCRIPT_DIR%"
)

echo [4/6] Starting Django Backend on 8000...
cd /d "%SCRIPT_DIR%backend"
start /b cmd /c "python manage.py runserver 0.0.0.0:8000 > ..\logs\backend.log 2>&1"
cd /d "%SCRIPT_DIR%"

echo [5/6] Starting Frontend App on 5173...
cd /d "%SCRIPT_DIR%frontend"
start /b cmd /c "npm run dev -- --host 0.0.0.0 --port 5173 > ..\logs\frontend.log 2>&1"
cd /d "%SCRIPT_DIR%"

echo [6/6] Starting Virtual Meter live data feed...
cd /d "%SCRIPT_DIR%Admin"
start /b cmd /c "python -X utf8 virtual_meter_gov.py > ..\logs\virtual_meter_gov.log 2>&1"
cd /d "%SCRIPT_DIR%"

echo.
echo Waiting for services to initialize...
timeout /t 8 /nobreak >nul

echo.
echo ============================================
echo    Services Started
echo ============================================
echo    App + Admin   : http://localhost:5173  (admin at /admin)
echo    Backend API   : http://localhost:8000/api/v1/
echo.
echo Logs:
echo    logs\backend.log
echo    logs\frontend.log
echo    logs\virtual_meter_gov.log
echo.
start http://localhost:5173/auth

echo Press any key to stop all services and exit...
pause >nul

echo.
echo Stopping services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /PID %%a /F 2>nul

echo All services stopped.
exit /b 0
