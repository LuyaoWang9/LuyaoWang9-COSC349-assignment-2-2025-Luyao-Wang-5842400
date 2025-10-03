#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx -y

# Create application directory in user home
mkdir -p /home/ubuntu/cloud-notebook/backend
cd /home/ubuntu/cloud-notebook/backend

# Copy your backend files from the correct backend directory
cp /home/ubuntu/LuyaoWang9-COSC349-assignment-2-2025-Luyao-Wang-5842400/backend/app.py ./

# Update the app.py to use port 8080 instead of 5054
sed -i 's/port=5054/port=8080/g' app.py
sed -i 's/:5054/:8080/g' app.py

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install flask flask-cors mysql-connector-python gunicorn

# Create backend service file with port 8080
sudo tee /etc/systemd/system/cloud-notebook-backend.service > /dev/null <<EOF
[Unit]
Description=Cloud Notebook Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cloud-notebook/backend
Environment=PATH=/home/ubuntu/cloud-notebook/backend/venv/bin
ExecStart=/home/ubuntu/cloud-notebook/backend/venv/bin/gunicorn --bind 0.0.0.0:8080 --timeout 120 --workers 2 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable cloud-notebook-backend
sudo systemctl start cloud-notebook-backend

# Wait a moment for the service to start
sleep 5

# Check status
echo "=== Checking Backend Service Status ==="
sudo systemctl status cloud-notebook-backend --no-pager

# Test the backend on port 8080
echo "=== Testing Backend API ==="
sleep 2
curl -s http://localhost:8080/health | head -20

echo "✅ Backend deployment complete!"
echo "🌐 Backend API available at: http://$(curl -s ifconfig.me):8080"