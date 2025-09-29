#!/bin/bash
set -e

echo "Starting frontend deployment..."

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
cd /home/ec2-user/shared-expense-manager/frontend
nohup /usr/bin/python3 -m gunicorn -w 2 -b 0.0.0.0:5050 app:app > /var/log/expense-frontend.log 2>&1 &

echo "Frontend started!"
echo "Check logs: tail -f /var/log/expense-frontend.log"
echo "Access at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5050"