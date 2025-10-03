#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx -y

# Create application directory
sudo mkdir -p /opt/cloud-notebook/backend
cd /opt/cloud-notebook/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install flask flask-cors mysql-connector-python

# Create backend service file for port 8080
sudo tee /etc/systemd/system/cloud-notebook-backend.service > /dev/null <<EOF
[Unit]
Description=Cloud Notebook Backend (Port 8080)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/cloud-notebook/backend
Environment=PATH=/opt/cloud-notebook/backend/venv/bin
ExecStart=/opt/cloud-notebook/backend/venv/bin/python3 app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable cloud-notebook-backend
sudo systemctl start cloud-notebook-backend

# Update security group reminder
echo "✅ Backend deployment complete!"
echo "📝 REMEMBER: Update EC2 Security Group to allow inbound traffic on port 8080"
echo "🌐 Backend API available at: http://\$(curl -s ifconfig.me):8080"
echo "🔧 Backend Health: http://\$(curl -s ifconfig.me):8080/health"