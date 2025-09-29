#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
sudo sed -i 's/^bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf || true
sudo systemctl enable mysql
sudo systemctl restart mysql
sudo mysql -e "CREATE DATABASE IF NOT EXISTS expenses;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'expense_user'@'%' IDENTIFIED WITH mysql_native_password BY 'password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON expenses.* TO 'expense_user'@'%'; FLUSH PRIVILEGES;"
sudo mysql expenses < /vagrant/db/init.sql
