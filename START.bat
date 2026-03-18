@echo off
REM Rocket Landing Simulator - Quick Start Script (Windows)
REM This script starts both backend and frontend servers

setlocal enabledelayedexpansion

cls
echo.
echo ============================================================
echo   AI ROCKET LANDING SIMULATOR - Quick Start
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install Node.js
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo Checking dependencies...
echo.

REM Get to project root
cd /d "%~dp0"

REM Check backend files
if not exist "backend\main.py" (
    echo ERROR: backend\main.py not found
    pause
    exit /b 1
)

REM Check frontend files
if not exist "frontend\package.json" (
    echo ERROR: frontend\package.json not found
    pause
    exit /b 1
)

echo   Python: OK
echo   Node.js: OK
echo   Backend: OK
echo   Frontend: OK
echo.

REM Start backend in new window
echo Starting backend server on http://localhost:10000/
echo.
start "Rocket Landing Simulator - Backend" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 10000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start frontend in new window
echo Starting frontend server on http://localhost:5173/
echo.
start "Rocket Landing Simulator - Frontend" cmd /k "cd frontend && npm run dev"

REM Wait for frontend to start
timeout /t 3 /nobreak

echo.
echo ============================================================
echo   SERVERS STARTING...
echo ============================================================
echo.
echo Frontend: http://localhost:5173/
echo Backend:  http://localhost:10000/
echo API Docs: http://localhost:10000/docs
echo.
echo Waiting for servers to fully start (this may take 10-15 seconds)...
echo.

REM Wait and try to open in browser
timeout /t 5 /nobreak

echo Opening application in browser...
start http://localhost:5173/

echo.
echo ============================================================
echo   SUCCESS! Application is running
echo ============================================================
echo.
echo Next steps:
echo 1. Wait for browser to open automatically
echo 2. Click "Start Simulation" to run the rocket landing
echo 3. Try "Step Mode" for manual control
echo 4. Watch the real-time metrics panel
echo.
echo To stop:
echo - Close the backend and frontend windows
echo - Or press Ctrl+C in each window
echo.
echo ============================================================
echo.

pause
