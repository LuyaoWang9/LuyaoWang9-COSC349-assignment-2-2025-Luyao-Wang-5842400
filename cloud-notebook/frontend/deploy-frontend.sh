#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install nginx
sudo apt install nginx -y

# Create web directory
sudo mkdir -p /var/www/cloud-notebook
cd /var/www/cloud-notebook

# Get backend IP (you'll need to update this)
BACKEND_IP="YOUR_BACKEND_IP_HERE"  # ⚠️ UPDATE THIS

# Create nginx configuration
sudo tee /etc/nginx/sites-available/cloud-notebook > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    root /var/www/cloud-notebook;
    index index.html;

    # Frontend files
    location / {
        try_files \$uri \$uri/ =404;
    }

    # API proxy to backend
    location /api/ {
        proxy_pass http://$BACKEND_IP:5054/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://$BACKEND_IP:5054/health;
        proxy_set_header Host \$host;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/cloud-notebook /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl enable nginx

echo "✅ Frontend deployment complete!"
echo "🌐 Frontend available at: http://$(curl -s ifconfig.me)"