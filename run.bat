@echo off
title E-Commerce Business Intelligence & Customer Analytics Dashboard
echo =================================================================
echo   Starting E-Commerce Business & Customer Intelligence Platform
echo =================================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not found in your PATH. Please install Python 3.10+ and try again.
    pause
    exit /b 1
)

:: 2. Check and install dependencies
echo [*] Checking and verifying dependencies...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check

:: 3. Check and initialize database if needed
if not exist "data\processed\ecommerce.db" (
    echo [*] Initializing database and generating sample data...
    python data\download_or_generate_data.py
)

:: 4. Launch Streamlit Dashboard
echo.
echo [*] Launching interactive dashboard...
echo [*] Your browser will open automatically at http://localhost:8501
echo.
streamlit run dashboard\app.py

pause
