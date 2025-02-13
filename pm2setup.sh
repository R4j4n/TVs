sudo apt update && sudo apt upgrade -y

# Install Node.js from NodeSource (LTS version)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify Node.js and npm installation
node -v
npm -v

# Install PM2 globally
sudo npm install -g pm2

# Verify PM2 installation
pm2 -v

# Set up PM2 to start on boot
pm2 startup

# Output instructions for enabling PM2 startup
echo "Copy and run the command shown above to enable PM2 on startup."

echo "Installation complete! Node.js, npm, and PM2 are ready to use."
