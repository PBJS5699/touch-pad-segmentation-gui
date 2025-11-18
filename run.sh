#!/bin/bash
# Launcher script for Cell Segmentation Tool

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
python -c "import PyQt5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the application
echo "Starting Cell Segmentation Tool..."
python cell_segmentation_tool.py


