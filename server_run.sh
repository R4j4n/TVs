#!/bin/bash

# Variables
SERVICE_NAME="tv_server_api"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
CWD=$(pwd)
USER=$(whoami)
PYTHON_EXEC="$CWD/venv/bin/python3"
SCRIPT_PATH="$CWD/server/streaming_api.py"

# Step 1: Create the systemd service file
echo "Creating systemd service file at $SERVICE_FILE..."

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=TV Automation Script
After=network.target

[Service]
Type=simple
WorkingDirectory=$CWD
ExecStart=$PYTHON_EXEC $SCRIPT_PATH
Restart=always
User=$USER
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOL

echo "Systemd service file created successfully."

# Step 2: Reload systemd to recognize the new service
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Step 3: Enable the service to start on boot
echo "Enabling the $SERVICE_NAME service..."
sudo systemctl enable $SERVICE_NAME.service

# Step 4: Start the service immediately
echo "Starting the $SERVICE_NAME service..."
sudo systemctl start $SERVICE_NAME.service

# Step 5: Check the status of the service
echo "Checking the service status..."
sudo systemctl status $SERVICE_NAME.service --no-pager

echo "Service setup complete!"
