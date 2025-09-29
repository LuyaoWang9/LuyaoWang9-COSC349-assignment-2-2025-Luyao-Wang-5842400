#!/bin/bash
set -e

echo "Starting dashboard deployment..."

# Update system
sudo yum update -y
sudo yum install -y python3 python3-pip

# Install Python dependencies
sudo pip3 install -r requirements.txt gunicorn

# Set environment variables
export DB_HOST=shared-expense-db.cscpnqmixnxc.us-east-1.rds.amazonaws.com
export DB_USER=admin
export DB_PASS=ExpenseApp2025!
export DB_NAME=expenses

# Start the application directly (for now)
cd /home/ec2-user/shared-expense-manager/dashboard
nohup /usr/bin/python3 -m gunicorn -w 2 -b 0.0.0.0:6000 dashboard:app > /var/log/expense-dashboard.log 2>&1 &

echo "Dashboard started!"
echo "Check logs: tail -f /var/log/expense-dashboard.log"
echo "Access at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):6000"
