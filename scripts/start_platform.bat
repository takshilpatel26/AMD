@echo off
REM ============================================
REM Gram Meter Platform - One-Click Startup
REM ============================================
REM This script starts all services:
REM 1. Django Backend (port 8000)
REM 2. Frontend User App (port 5173)
REM 3. Admin route in Frontend (/admin)
REM ============================================

title Gram Meter Platform
color 0A

echo.
echo ============================================
echo    🌾 Gram Meter Platform Startup
echo ============================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Create logs directory if not exists
if not exist "logs" mkdir logs
if not exist ".pids" mkdir .pids

echo [1/5] Cleaning up old processes...
REM Kill processes on ports
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /PID %%a /F 2>nul
timeout /t 2 /nobreak >nul

echo [2/5] Activating Python virtual environment...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r backend\requirements.txt
)

echo [3/5] Starting Django Backend on port 8000...
cd /d "%SCRIPT_DIR%backend"
start /b cmd /c "python manage.py runserver 0.0.0.0:8000 > "%SCRIPT_DIR%logs\backend.log" 2>&1"
cd /d "%SCRIPT_DIR%"

echo [4/5] Starting Frontend User App on port 5173...
cd /d "%SCRIPT_DIR%frontend"
start /b cmd /c "npm run dev > "%SCRIPT_DIR%logs\frontend.log" 2>&1"
cd /d "%SCRIPT_DIR%"

echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

echo.
echo ============================================
echo    ✅ All Services Starting!
echo ============================================
echo.
echo    🌐 User App:      http://localhost:5173
echo    🔧 Admin Route:   http://localhost:5173/admin
echo    🖥️  Backend API:   http://localhost:8000/api/v1/
echo.
echo 📋 Admin Login Credentials:
echo    Username: admin
echo    Password: admin123
echo.
echo 📋 Test User Credentials:
echo    Phone: 9876543210 (farmer_ramesh)
echo    Phone: 9876543211 (farmer_priya)
echo.
echo 📁 Logs are available at:
echo    - logs\backend.log
echo    - logs\frontend.log
echo.
echo ============================================
echo.

REM Open browser
timeout /t 3 /nobreak >nul
start http://localhost:5173
start http://localhost:5173/admin

echo Press any key to stop all services and exit...
pause >nul

echo.
echo 🛑 Stopping all services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /PID %%a /F 2>nul

echo All services stopped.
exit /b 0
