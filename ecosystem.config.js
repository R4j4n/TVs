module.exports = {
  apps: [
    {
      name: 'python-server',  // Name of your PM2 process
      script: 'server/server.py',  // Path to your Python script
      interpreter: './venv/bin/python',  // Path to Python interpreter in virtual environment
      
      // Process configuration
      instances: 1,  // Number of instances to launch
      autorestart: true,  // Auto restart if app crashes
      watch: false,  // Watch for file changes
      max_memory_restart: '800M',  // Restart if memory exceeds 1GB
      
      // Environment variables
      env: {
        NODE_ENV: 'development',
        PYTHONUNBUFFERED: '1'  // Ensures Python output is sent to PM2 logs immediately
      },
      
      env_production: {
        NODE_ENV: 'production',
        PYTHONUNBUFFERED: '1'
      },
      
      // Error and output logs
      error_file: 'logs/python-server-error.log',
      out_file: 'logs/python-server-out.log',
      merge_logs: true,
      
      // Time-based restart
      cron_restart: '0 0 * * *',  // Restart at midnight every day
      
      // Retry strategy
      max_restarts: 10,
      min_uptime: '10s',
      
      // Misc settings
      kill_timeout: 3000,  // Time in ms to wait before forcing process kill
      restart_delay: 3000  // Time in ms to wait between restarts
    }
  ]
};
