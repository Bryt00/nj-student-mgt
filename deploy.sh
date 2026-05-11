#!/bin/bash

# EDUANALYTICS - Production Deployment Script
# Usage: ./deploy.sh

echo "🚀 Starting EduAnalytics Deployment..."

# 1. Update code (Assumes Git is used)
# git pull origin main

# 2. Virtual Environment Management
if [ ! -d "venv" ]; then
    echo "🌐 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔌 Activating virtual environment..."
source venv/bin/activate

# 3. Install/Update dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Apply migrations
echo "🗄️ Running database migrations..."
python3 manage.py migrate --noinput

# 5. Collect static files
echo "🎨 Collecting static assets..."
mkdir -p static
python3 manage.py collectstatic --noinput

# 6. (Optional) Update Systemd & Nginx Configuration
# Run this once or if your paths change
# USAGE: ./deploy.sh --setup

if [[ "$1" == "--setup" ]]; then
    echo "⚙️ Setting up Systemd & Nginx..."
    
    USER=$(whoami)
    PROJECT_DIR=$(pwd)
    
    # Create Systemd Service
    cat <<EOF | sudo tee /etc/systemd/system/student_mgt.service
[Unit]
Description=Gunicorn instance to serve EduAnalytics
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:$PROJECT_DIR/student_mgt.sock \
          school_system.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

    # Create Nginx Config
    cat <<EOF | sudo tee /etc/nginx/sites-available/student_mgt
server {
    listen 80;
    server_name studentmgt.njuascogh.org;

    client_max_body_size 20M;

    location / {
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$http_x_forwarded_proto;
        proxy_pass http://unix:$PROJECT_DIR/student_mgt.sock;
    }

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/student_mgt /etc/nginx/sites-enabled/
    sudo systemctl daemon-reload
    sudo systemctl enable student_mgt
    sudo systemctl restart student_mgt
    sudo systemctl restart nginx
    echo "✨ Systemd & Nginx updated and restarted!"
fi

echo "✅ Deployment Complete! System is live at studentmgt.njuascogh.org"
