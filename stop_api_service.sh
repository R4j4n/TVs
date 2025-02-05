#!/bin/bash

# Script name: stop_api_service.sh

# Function to check if tmux session exists
session_exists() {
    tmux has-session -t api_service 2>/dev/null
}

# Check if the session exists
if session_exists; then
    echo "Stopping API service..."
    
    # Send Ctrl+C to gracefully stop the Python process
    tmux send-keys -t api_service C-c
    
    # Wait a moment for the process to stop
    sleep 2
    
    # Kill the tmux session
    tmux kill-session -t api_service
    
    echo "API service stopped successfully"
else
    echo "API service is not running"
fi

# Optional: Remove from crontab if you want to prevent restart on reboot
if [ "$1" == "--disable-autostart" ]; then
    crontab -l | grep -v "start_api_service.sh" | crontab -
    echo "Autostart disabled"
fi