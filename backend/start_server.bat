@echo off
echo Starting PageIndex Chat Backend...
echo.

cd /d %~dp0

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Check Python
python --version
if errorlevel 1 (
    echo Python not found!
    pause
    exit /b 1
)

REM Run server
python run.py

pause




