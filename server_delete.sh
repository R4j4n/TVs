#!/bin/bash

# Variables
SERVICE_NAME="tv_server_api"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

# Step 1: Stop the service if running
echo "Stopping the $SERVICE_NAME service..."
sudo systemctl stop $SERVICE_NAME.service

# Step 2: Disable the service to prevent it from starting on boot
echo "Disabling the $SERVICE_NAME service..."
sudo systemctl disable $SERVICE_NAME.service

# Step 3: Remove the service file
if [ -f "$SERVICE_FILE" ]; then
    echo "Removing the service file: $SERVICE_FILE"
    sudo rm "$SERVICE_FILE"
else
    echo "Service file not found: $SERVICE_FILE"
fi

# Step 4: Reload systemd to apply changes
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Step 5: Remove lingering service files
echo "Clearing systemd service cache..."
sudo systemctl reset-failed

echo "Service $SERVICE_NAME has been completely removed."
