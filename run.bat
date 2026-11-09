@echo off
title E-Commerce Business Intelligence Platform
echo =================================================================
echo   Starting E-Commerce Business and Customer Intelligence Platform
echo =================================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not detected in your PATH. Please install Python 3.10+ and re-run.
    pause
    exit /b 1
)

:: 2. Check and install dependencies
echo [*] Verifying project dependencies...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check

:: 3. Check and initialize database if needed
if not exist "data\processed\ecommerce.db" (
    echo [*] Initializing local database...
    python data\download_or_generate_data.py
)

:: 4. Launch Streamlit Dashboard
echo.
echo [*] Starting dashboard application...
echo.
streamlit run dashboard\app.py

pause
