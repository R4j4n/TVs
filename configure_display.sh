CMDLINE_FILE="/boot/firmware/cmdline.txt"
VIDEO_PARAM="video=HDMI-A-1:1920x1080@60"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Check if file exists
if [ ! -f "$CMDLINE_FILE" ]; then
    echo "Error: $CMDLINE_FILE not found!"
    exit 1
fi

# Create backup
cp "$CMDLINE_FILE" "${CMDLINE_FILE}.backup"
echo "Backup created at ${CMDLINE_FILE}.backup"

# Check if parameter already exists
if grep -q "$VIDEO_PARAM" "$CMDLINE_FILE"; then
    echo "Video parameter already exists in cmdline.txt"
    exit 0
fi

# Read current content, remove trailing whitespace, and append new parameter
content=$(cat "$CMDLINE_FILE" | tr -d '\n')
echo "${content% } ${VIDEO_PARAM}" > "$CMDLINE_FILE"

echo "Successfully added video parameter to cmdline.txt"
echo "Please reboot your system for changes to take effect"