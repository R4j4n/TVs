[Unit] 

Description=TV Automation Script 

After=network.target 

 

[Service] 

Type=simple 

WorkingDirectory=/home/snackshack_left/automation 

ExecStart=/home/snackshack_left/automation/venv/bin/python /home/snackshack_left/automation/tv.py 

Restart=always 

User=snackshack_left 

 

[Install] 

WantedBy=multi-user.target 

 
