#!/bin/bash

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass is not installed. Please install it first:"
    echo "Ubuntu/Debian: sudo apt-get install sshpass"
    echo "macOS: brew install hudochenkov/sshpass/sshpass"
    exit 1
fi

# Configuration - Add your Raspberry Pi details here
USERNAME1="snackshack1"
HOST1="10.0.0.81"
PASS1="r4j4n"

USERNAME2="snackshackpromo"
HOST2="10.0.0.157"
PASS2="r4j4n"

# Git repository path on the Pis
GIT_PATH="~/TVs"

# Function to print section header
print_header() {
    echo "
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🚀 $1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to update a single Pi
update_pi() {
    local username=$1
    local host=$2
    local password=$3
    
    print_header "📡 Updating $username@$host"
    
    # Try to connect and run commands
    sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username@$host" "
        # Navigate to repository
        cd $GIT_PATH
        if [ \$? -ne 0 ]; then
            echo '❌ Failed to change directory'
            exit 1
        fi
        
        echo '📥 Pulling latest changes...'
        git pull
        if [ \$? -ne 0 ]; then
            echo '❌ Git pull failed'
            exit 1
        fi

        echo '🔄 Restarting python-server PM2 instance as root...'
        # Ensure PM2 is using root's process list
        sudo -H pm2 reload python-server --update-env
        if [ \$? -ne 0 ]; then
            echo '❌ PM2 reload failed'
            exit 1
        fi
        
        # Save PM2 process list for root
        sudo -H pm2 save
        
        echo '✅ Update completed successfully'
    "

    if [ $? -eq 0 ]; then
        echo "✅ Successfully updated $username@$host"
        return 0
    else
        echo "❌ Failed to update $username@$host"
        return 1
    fi
}

# Main execution
print_header "Starting update process for all Raspberry Pis"
failed=0

# Update first Pi
echo "🔄 Updating first Pi..."
update_pi "$USERNAME1" "$HOST1" "$PASS1"
if [ $? -ne 0 ]; then
    failed=$((failed + 1))
fi

# Update second Pi
echo "🔄 Updating second Pi..."
update_pi "$USERNAME2" "$HOST2" "$PASS2"
if [ $? -ne 0 ]; then
    failed=$((failed + 1))
fi

# Report summary
print_header "📊 Update Summary"
echo "📌 Total Pis: 2"
echo "❌ Failed updates: $failed"
echo "✅ Successful updates: $((2 - failed))"

if [ $failed -gt 0 ]; then
    echo "❌ Some updates failed!"
    exit 1
else
    echo "
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🎉 All updates completed successfully! 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi