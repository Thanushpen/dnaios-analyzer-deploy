@echo off
REM DNAiOS Analyzer Quick Start Script for Windows
setlocal enabledelayedexpansion

echo ╔════════════════════════════════════════════════════════════╗
echo ║   🧬 DNAiOS Architecture Analyzer - Quick Start           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check Python installation
echo 📋 Checking prerequisites...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is not installed
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed
    pause
    exit /b 1
)
echo ✅ pip found

REM Create virtual environment
echo.
echo 🔧 Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ⚠️  Virtual environment already exists
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install backend dependencies
echo.
echo 📦 Installing backend dependencies...
cd backend
pip install -r requirements.txt
echo ✅ Dependencies installed

REM Start backend
echo.
echo 🚀 Starting backend server...
echo Backend will run on http://localhost:5001
echo.
start /b python analyzer.py

REM Wait for backend to start
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend
echo.
echo 🎨 Starting frontend server...
cd ..\frontend
echo Frontend will run on http://localhost:8000
echo.
start /b python -m http.server 8000

REM Wait for frontend to start
timeout /t 2 /nobreak >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    🎉 ALL SET!                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Backend:  http://localhost:5001
echo Frontend: http://localhost:8000
echo.
echo Open your browser and visit: http://localhost:8000
echo.
echo Press any key to stop the servers...
pause >nul

REM Stop servers
taskkill /F /IM python.exe /T >nul 2>&1
echo Done!
