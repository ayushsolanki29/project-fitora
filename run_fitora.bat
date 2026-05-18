@echo off
title FITORA - Smart Tailoring System
cd /d "%~dp0"

echo ============================================
echo   FITORA - Starting Project
echo ============================================
echo.

REM --- Python check ---
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed.
    echo Download Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM --- Virtual environment ---
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

REM --- Install dependencies ---
echo Installing dependencies...
pip install -r requirements.txt -q

REM --- Environment file ---
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from .env.example ...
        copy .env.example .env
        echo Please edit .env and add your API keys, then run this file again.
        pause
        exit /b 0
    )
)

REM --- Database ---
echo Running migrations...
python manage.py migrate --noinput

echo Seeding sample data...
python manage.py seed_fitora

REM --- Start server ---
echo.
echo Starting server at http://127.0.0.1:8000
echo.
start "FITORA Server" cmd /k ".venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000"

REM --- Wait for server ---
timeout /t 4 /nobreak >nul

REM --- Open browsers ---
start http://127.0.0.1:8000/
start http://127.0.0.1:8000/tailors/
start http://127.0.0.1:8000/book-tailor/
start http://127.0.0.1:8000/login/
start http://127.0.0.1:8000/customer/
start http://127.0.0.1:8000/adminpanel/
start http://127.0.0.1:8000/tailor/

echo.
echo ============================================
echo   FITORA is running!
echo ============================================
echo.
echo   Website:       http://127.0.0.1:8000/
echo   Customer:      http://127.0.0.1:8000/customer/
echo   Admin Panel:   http://127.0.0.1:8000/adminpanel/
echo   Tailor Portal: http://127.0.0.1:8000/tailor/
echo.
echo   Demo Login: demo@fitora.com / Customer@123
echo.
echo   AI Chatbot: Click the chat button bottom-right
echo   Payments:   Stripe test mode enabled
echo.
echo   Close the "FITORA Server" window to stop.
echo ============================================
pause
