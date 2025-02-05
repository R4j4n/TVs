#!/bin/bash

# Script name: setup_autostart.sh

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Make the start script executable
chmod +x "${SCRIPT_DIR}/start_api_service.sh"

# Add to crontab if not already present
if ! crontab -l | grep -q "start_api_service.sh"; then
    (crontab -l 2>/dev/null; echo "@reboot ${SCRIPT_DIR}/start_api_service.sh") | crontab -
    echo "Added start_api_service.sh to crontab"
else
    echo "start_api_service.sh is already in crontab"
fi

echo "Setup complete. The API service will now start automatically on reboot."