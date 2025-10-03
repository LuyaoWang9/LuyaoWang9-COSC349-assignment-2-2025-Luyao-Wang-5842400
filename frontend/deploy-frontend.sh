# Update system
sudo apt update && sudo apt upgrade -y

# Install nginx
sudo apt install nginx -y

# Create web directory
sudo mkdir -p /var/www/cloud-notebook
cd /var/www/cloud-notebook

# Get backend IP (you'll need to update this)
BACKEND_IP="ec2-54-157-241-129.compute-1.amazonaws.com"  # ⚠️ UPDATE THIS

# Create nginx configuration
sudo tee /etc/nginx/sites-available/cloud-notebook > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    root /var/www/cloud-notebook;
    index index.html;

    # Frontend files
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API proxy to backend
    location /api/ {
        proxy_pass http://$BACKEND_IP:5054/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Additional proxy settings for better compatibility
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://$BACKEND_IP:5054/health;
        proxy_set_header Host \$host;
    }

    # Static assets cache
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
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

# Get public IP safely
PUBLIC_IP=$(curl -s -f ifconfig.me || curl -s -f ipinfo.io/ip || echo "unknown")

echo "✅ Frontend deployment complete!"
echo "🌐 Frontend available at: http://$PUBLIC_IP"
echo "🔧 Backend configured to: $BACKEND_IP:8080"
echo "📁 Web directory: /var/www/cloud-notebook"