@echo off
REM Launcher script for Cell Segmentation Tool (Windows)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run the application
echo Starting Cell Segmentation Tool...
python cell_segmentation_tool.py

pause


