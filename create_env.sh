#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check and install Python3 and pip if not installed
if command_exists python3 && command_exists pip3; then
    echo "Python3 and pip3 are already installed."
else
    echo "Installing Python3 and pip3..."
    sudo apt update && sudo apt install -y python3-pip
fi

# Check and install FFmpeg if not installed
if command_exists ffmpeg; then
    echo "FFmpeg is already installed."
else
    echo "Installing FFmpeg..."
    sudo apt update && sudo apt install -y ffmpeg
fi


if command_exists vlc; then
    echo "VLC is already installed."
else
    echo "Installing VLC..."
    sudo apt update && sudo apt install -y vlc
fi

if command_exists cec-utils; then
    echo "cec-utils is already installed."
else
    echo "Installing cec-utils..."
    sudo apt update && sudo apt install -y cec-utils
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found!"
fi

echo "Setup complete. Virtual environment is activated."
