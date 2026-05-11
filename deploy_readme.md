# EduAnalytics Deployment Guide

This document provides instructions for deploying the School Management System to a production environment.

## 1. Environment Setup
Create a `.env` file in the root directory on the server:
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,server-ip
```

## 2. Running the Deploy Script
Give execution permissions to the script:
```bash
chmod +x deploy.sh
./deploy.sh
```

## 3. Server Configuration (Nginx/Gunicorn)
We recommend using **Gunicorn** as the WSGI server and **Nginx** as a reverse proxy.

### Sample Gunicorn Command:
```bash
gunicorn --workers 3 --bind unix:/home/user/school_system.sock school_system.wsgi:application
```

### Static Files
The system uses **WhiteNoise** to serve static files. After running `collectstatic`, all assets will be stored in the `staticfiles/` directory. No extra Nginx configuration is required for static files, but it is recommended for performance.

## 4. Database
For production, we recommend migrating from SQLite to **PostgreSQL**. Update the `DATABASES` setting in `settings.py` or use `DATABASE_URL` with `django-environ`.
