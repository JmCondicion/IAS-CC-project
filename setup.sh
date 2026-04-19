#!/bin/bash

echo "Setting up Python virtual environment for QR Attendance System..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "Virtual environment created and dependencies installed successfully!"
echo "Activate it using: source venv/bin/activate"
echo "Then run: flask db upgrade && flask run"
