#!/bin/bash

# Update system
sudo yum update -y

# Install Python and pip
sudo yum install -y python3 python3-pip

# Install application dependencies
pip3 install flask pymysql flask-cors

# Create application directory
mkdir -p /home/ec2-user/task-manager
cd /home/ec2-user/task-manager

# Create systemd service file
sudo cat > /etc/systemd/system/taskmanager.service << EOF
[Unit]
Description=Task Manager Backend
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/task-manager
ExecStart=/usr/bin/python3 app.py
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable taskmanager
sudo systemctl start taskmanager

# Check service status
sudo systemctl status taskmanager