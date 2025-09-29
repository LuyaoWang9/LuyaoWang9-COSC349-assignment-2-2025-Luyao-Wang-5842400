#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv
python3 -m venv /home/vagrant/venv
/home/vagrant/venv/bin/pip install --upgrade pip
/home/vagrant/venv/bin/pip install -r /vagrant/dashboard/requirements.txt gunicorn
sudo tee /etc/systemd/system/dashboard.service >/dev/null <<'EOF'
[Unit]
Description=Shared Expense Dashboard
After=network.target
[Service]
User=vagrant
WorkingDirectory=/vagrant/dashboard
Environment=DB_HOST=192.168.56.10
Environment=DB_USER=expense_user
Environment=DB_PASS=password
Environment=DB_NAME=expenses
ExecStart=/home/vagrant/venv/bin/gunicorn -b 0.0.0.0:6000 dashboard:app
Restart=always
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable dashboard
sudo systemctl restart dashboard
