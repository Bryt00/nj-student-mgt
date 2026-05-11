#!/bin/bash

# EDUANALYTICS - Production Deployment Script
# Usage: ./deploy.sh

echo "🚀 Starting EduAnalytics Deployment..."

# 1. Update code (Assumes Git is used)
# git pull origin main

# 2. Activate virtual environment (Change path as needed)
# source venv/bin/activate

# 3. Install/Update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# 4. Apply migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# 5. Collect static files
echo "🎨 Collecting static assets..."
python manage.py collectstatic --noinput

# 6. Clear cache (optional but recommended)
# python manage.py clear_cache

# 7. Restart Application Server
# This depends on your setup (Systemd, Supervisor, etc.)
# echo "♻️ Restarting Gunicorn..."
# sudo systemctl restart eduanalytics

echo "✅ Deployment Complete! System is live."
