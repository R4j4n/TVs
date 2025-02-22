#!/bin/bash

# Check if all required arguments are provided
if [ "$#" -ne 3 ]; then
    echo "🚫 Usage: $0 <ip_address> <username> <password>"
    exit 1
fi

IP=$1
USERNAME=$2
PASSWORD=$3

# Function to handle errors
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Function to print section header
print_header() {
    echo "
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🚀 $1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to print success message
print_success() {
    echo "✅ $1"
}

# Function to print info message
print_info() {
    echo "ℹ️  $1"
}

# Function to execute SSH commands
execute_ssh_command() {
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USERNAME@$IP" "$1" || handle_error "Failed to execute: $1"
}

print_header "Starting deployment on $IP"

# Create dynamic command check function on remote
execute_ssh_command '
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

print_step() {
    echo "📍 $1"
}

# Check and install git if not installed
if command_exists git; then
    print_step "Git is already installed"
else
    print_step "Installing git..."
    sudo apt-get update && sudo apt-get install -y git
fi

# Remove existing TVs directory if it exists
if [ -d "TVs" ]; then
    print_step "🗑️  Cleaning up: Removing existing TVs directory..."
    rm -rf TVs
fi
'

print_header "📥 Cloning Repository"
execute_ssh_command "git clone https://github.com/R4j4n/TVs"
execute_ssh_command "cd TVs && git checkout backend_dev"

print_header "🛠️  Running Setup Scripts"
execute_ssh_command '
cd TVs

# Make scripts executable
chmod +x configure_display.sh create_env.sh pm2setup.sh

# Check and run configure_display.sh
if [ -f "configure_display.sh" ]; then
    echo "🔧 Running configure_display.sh..."
    sudo ./configure_display.sh
else
    echo "❌ Error: configure_display.sh not found"
    exit 1
fi

# Check and run create_env.sh
if [ -f "create_env.sh" ]; then
    echo "🌱 Running create_env.sh..."
    sudo ./create_env.sh
else
    echo "❌ Error: create_env.sh not found"
    exit 1
fi

# Check and run pm2setup.sh
if [ -f "pm2setup.sh" ]; then
    echo "⚙️  Running pm2setup.sh..."
    sudo ./pm2setup.sh
else
    echo "❌ Error: pm2setup.sh not found"
    exit 1
fi
'

print_header "🎉 Installation Complete!"

print_header "📊 Checking installation Status"
execute_ssh_command "pm2 list"

echo "
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🌟 All tasks completed successfully! 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"