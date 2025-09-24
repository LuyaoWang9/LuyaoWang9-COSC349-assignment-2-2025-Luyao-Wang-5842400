#!/bin/bash
echo "Starting web server deployment on EC2..."

# Update and install dependencies
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv nginx git

# Install AWS CLI for S3 access
sudo apt-get install -y awscli

# Create app directory
sudo mkdir -p /opt/expense-manager
sudo chown -R ubuntu:ubuntu /opt/expense-manager
cd /opt/expense-manager

# Clone your repository
git clone https://github.com/LuyaoWang9/COSC349-assignment2.git .

# Set up Python environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install boto3 requests

# Configure environment
cat > .env << EOF
DB_HOST=your-rds-endpoint
DB_USER=expense_user
DB_PASS=your-password
DB_NAME=expenses
API_SERVER_URL=http://api-server-private-ip:8000
S3_BUCKET=expense-receipts-bucket
SECRET_KEY=your-secret-key-here
AWS_REGION=us-east-1
EOF

# Set up nginx
sudo tee /etc/nginx/sites-available/expense-manager << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5050;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /static {
        alias /opt/expense-manager/static;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/expense-manager /etc/nginx/sites-enabled/
sudo systemctl enable nginx
sudo systemctl restart nginx

# Create systemd service
sudo tee /etc/systemd/system/expense-web.service << EOF
[Unit]
Description=Expense Manager Web Frontend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/expense-manager
Environment=PATH=/opt/expense-manager/venv/bin
ExecStart=/opt/expense-manager/venv/bin/gunicorn -b 127.0.0.1:5050 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable expense-web
sudo systemctl start expense-web

echo "Web server deployment completed!"