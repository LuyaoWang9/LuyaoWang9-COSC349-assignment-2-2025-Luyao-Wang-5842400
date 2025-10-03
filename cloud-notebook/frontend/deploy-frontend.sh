# [file name]: deploy-frontend-dns.sh
#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install nginx
sudo apt install nginx -y

# Create web directory
sudo mkdir -p /var/www/cloud-notebook
cd /var/www/cloud-notebook

# Use DNS name instead of IP
BACKEND_DNS="ec2-3-208-22-181.compute-1.amazonaws.com"  # Your EC2 public DNS
BACKEND_PORT="8080"

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
        proxy_pass http://$BACKEND_DNS:$BACKEND_PORT/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://$BACKEND_DNS:$BACKEND_PORT/health;
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

echo "✅ Frontend deployment complete with DNS!"
echo "🌐 Frontend available at: http://\$(curl -s ifconfig.me)"