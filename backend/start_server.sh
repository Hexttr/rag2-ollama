#!/bin/bash
echo "Starting PageIndex Chat Backend..."
echo ""

cd "$(dirname "$0")"

# Activate virtual environment if exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Check Python
python3 --version || python --version || {
    echo "Python not found!"
    exit 1
}

# Run server
python3 run.py || python run.py




