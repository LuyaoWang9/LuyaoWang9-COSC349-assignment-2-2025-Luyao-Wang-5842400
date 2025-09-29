#!/bin/bash
set -e

echo "Starting dashboard deployment on port 6061..."

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

# Start the application on port 6061
cd /home/ec2-user/shared-expense-manager/dashboard
nohup python3 -m gunicorn -w 2 -b 0.0.0.0:6061 dashboard:app > dashboard.log 2>&1 &

echo "Dashboard started on port 6061!"
echo "Check: ps aux | grep gunicorn"
echo "Access: http://18.212.249.81:6061"