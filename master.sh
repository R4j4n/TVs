#!/bin/bash

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass is not installed. Please install it first:"
    echo "Ubuntu/Debian: sudo apt-get install sshpass"
    echo "macOS: brew install hudochenkov/sshpass/sshpass"
    exit 1
fi

# Configuration
# Format: "username hostname password"
PIHOSTS=(
    "testpi 10.0.0.156 YOUR_PASSWORD_1"
    "testpi2 10.0.0.155 YOUR_PASSWORD_2"
    # Add more Pis here in the same format
)

# Git repository path on the Pis (modify this to match your setup)
GIT_PATH="~/TVs"

# Function to check if SSH connection is successful
check_ssh() {
    local username=$1
    local host=$2
    local password=$3
    
    sshpass -p "$password" ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$username@$host" exit 2>/dev/null
    return $?
}

# Function to update a single Pi
update_pi() {
    local username=$1
    local host=$2
    local password=$3
    local full_host="$username@$host"
    
    echo "📡 Updating $full_host..."
    
    # Check SSH connection
    if ! check_ssh "$username" "$host" "$password"; then
        echo "❌ Failed to connect to $full_host"
        return 1
    }

    # Execute commands on the remote Pi
    sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$full_host" "
        cd $GIT_PATH || exit 1
        echo '📥 Pulling latest changes...'
        git pull
        if [ \$? -ne 0 ]; then
            echo '❌ Git pull failed'
            exit 1
        fi

        echo '🔄 Restarting python-server PM2 instance...'
        pm2 reload python-server
        if [ \$? -ne 0 ]; then
            echo '❌ PM2 reload failed'
            exit 1
        fi
        
        echo '✅ Update completed successfully'
    "

    if [ $? -eq 0 ]; then
        echo "✅ Successfully updated $full_host"
    else
        echo "❌ Failed to update $full_host"
        return 1
    fi
}

# Main execution
echo "🚀 Starting update process for all Raspberry Pis..."
failed_hosts=()

# Process each Pi
for host_info in "${PIHOSTS[@]}"; do
    # Split the host info into username, hostname, and password
    read -r username hostname password <<< "$host_info"
    
    if ! update_pi "$username" "$hostname" "$password"; then
        failed_hosts+=("$username@$hostname")
    fi
    echo "-----------------------------------"
done

# Report summary
echo "📊 Update Summary:"
echo "Total Pis: ${#PIHOSTS[@]}"
echo "Successfully updated: $((${#PIHOSTS[@]} - ${#failed_hosts[@]}))"

if [ ${#failed_hosts[@]} -gt 0 ]; then
    echo "❌ Failed updates (${#failed_hosts[@]}):"
    printf '%s\n' "${failed_hosts[@]}"
    exit 1
else
    echo "✅ All updates completed successfully!"
fi