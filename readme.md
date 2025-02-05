I'll create a shell script to safely stop the API service.



Save this script as `stop_api_service.sh` in the same directory as your other scripts. Here's how to use it:

1. Make it executable:
```bash
chmod +x stop_api_service.sh
```

2. To stop the service:
```bash
./stop_api_service.sh
```

3. To stop the service AND prevent it from starting on next reboot:
```bash
./stop_api_service.sh --disable-autostart
```

The script will:
1. Check if the API service is running
2. Send a graceful termination signal (Ctrl+C) to your Python process
3. Wait a moment for clean shutdown
4. Kill the tmux session
5. Optionally remove it from crontab if you use the --disable-autostart flag

If you ever need to check the status before stopping:
```bash
tmux ls
```

This will show you if the api_service session is running.

Would you like me to explain any part of this script in more detail?