#!/bin/bash
set -e

echo "Starting frontend deployment on port 5051..."

# Update system
sudo yum update -y
sudo yum install -y python3 python3-pip

# Install Python dependencies
sudo pip3 install -r requirements.txt gunicorn

# Kill any existing processes
sudo pkill -f python || true
sudo pkill -f gunicorn || true

# Set environment variables
export DB_HOST=shared-expense-db.cscpnqmixnxc.us-east-1.rds.amazonaws.com
export DB_USER=admin
export DB_PASS=ExpenseApp2025!
export DB_NAME=expenses

# Start the application on port 5051
cd /home/ec2-user/shared-expense-manager/frontend
nohup python3 -m gunicorn -w 2 -b 0.0.0.0:5051 app:app > frontend.log 2>&1 &

echo "Frontend started on port 5051!"
echo "Check: ps aux | grep gunicorn"
echo "Access: http://18.212.76.126:5051"