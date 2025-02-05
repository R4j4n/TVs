#!/bin/bash

# Script name: start_api_service.sh

# Function to check if tmux session exists
session_exists() {
    tmux has-session -t api_service 2>/dev/null
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if tmux is installed
if ! command_exists tmux; then
    echo "Installing tmux..."
    sudo apt update && sudo apt install -y tmux
fi

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "${SCRIPT_DIR}/venv/bin/activate"

# Create new tmux session if it doesn't exist
if ! session_exists; then
    # Create new detached session
    tmux new-session -d -s api_service

    # Send commands to the tmux session
    tmux send-keys -t api_service "cd ${SCRIPT_DIR}/server" C-m
    tmux send-keys -t api_service "source ../venv/bin/activate" C-m
    tmux send-keys -t api_service "python3 server.py" C-m
else
    echo "Session 'api_service' already exists"
fi

# Keep the session running in the background
tmux detach -s api_service