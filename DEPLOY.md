# Production Deployment Guide

This document outlines how to deploy Meet Your Modules to production.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Deployment Steps](#deployment-steps)
- [Production vs Development](#production-vs-development)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

---

## Overview

Meet Your Modules uses a **single-container production architecture** where:

- Flask backend serves both the API (`/api/*`) and frontend static files (`/`)
- Frontend is built during Docker image build (optimized, minified static files)
- Gzip compression is enabled for all responses
- Static assets have long-term caching headers (1 year for JS/CSS, 1 week for images)
- Database runs in a separate container with persistent volume

### Architecture Diagram

```
┌─────────────────────────────────────────┐
│  User Browser                           │
└──────────────┬──────────────────────────┘
               │ HTTP/HTTPS
               ▼
┌─────────────────────────────────────────┐
│  Flask App Container (Port 5000)        │
│  ┌─────────────────────────────────┐   │
│  │  Flask Backend                  │   │
│  │  - Serves /api/* endpoints      │   │
│  │  - Serves / for frontend        │   │
│  │  - Gzip compression enabled     │   │
│  │  - Cache headers configured     │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Frontend Static Files (/dist)  │   │
│  │  - Built from Vue + Vite        │   │
│  │  - Optimized & minified         │   │
│  │  - Hashed filenames             │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  PostgreSQL Container                   │
│  - Persistent data volume               │
└─────────────────────────────────────────┘
```

---

## Prerequisites

1. **Docker** and **Docker Compose** installed on server
2. **Domain name** (optional, but recommended)
3. **SSL/TLS certificate** (for HTTPS, recommended)
4. **Google Gemini API key** (for review moderation)
5. **Server** with minimum 2GB RAM, 10GB disk space

---

## Environment Configuration

### 1. Create Production Environment File

Create `.env.production` in the repository root:

```bash
# Database Configuration
DB_USER=module_guide
DB_PASSWORD=YOUR_SECURE_PASSWORD_HERE
DB_NAME=module_guide
DB_PORT=5432
DB_POOL_MIN=2
DB_POOL_MAX=10

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=YOUR_RANDOM_SECRET_KEY_HERE
BACKEND_PORT=5000

# Application Configuration
APP_PORT=5000  # Port to expose to host

# Google AI API
GOOGLE_API_KEY=your_gemini_api_key_here

# CORS Configuration (use your actual domain)
FRONTEND_ADDRESS=yourdomain.com
FRONTEND_PORT=443
FRONTEND_HTTPS=true

# Logging
LOG_LEVEL=INFO
```

### 2. Generate Secure Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate DB_PASSWORD
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Security Checklist

- [ ] Changed `DB_PASSWORD` from default
- [ ] Set a secure `SECRET_KEY`
- [ ] Configured `FRONTEND_ADDRESS` to your domain
- [ ] Set `FRONTEND_HTTPS=true` if using HTTPS
- [ ] `GOOGLE_API_KEY` is set and valid
- [ ] `.env.production` is **NOT** committed to git (already in `.gitignore`)

---

## Deployment Steps

### Option A: Simple Production Deployment

```bash
# 1. Clone repository
git clone https://github.com/yourusername/Meet-Your-Modules.git
cd Meet-Your-Modules

# 2. Create and configure .env.production (see above)
nano .env.production

# 3. Build and start production containers
docker-compose -f docker-compose.production.yml --env-file .env.production up -d --build

# 4. Check logs
docker-compose -f docker-compose.production.yml logs -f

# 5. Verify health
curl http://localhost:5000/api/health
curl http://localhost:5000/api/health/db
```

### Option B: Production with Nginx Reverse Proxy (Recommended)

For HTTPS and better performance, use Nginx as a reverse proxy:

1. **Install Nginx on host**:

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

2. **Configure Nginx** (`/etc/nginx/sites-available/module-guide`):

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL certificates (managed by certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy all requests to Flask container
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

3. **Enable site and get SSL certificate**:

```bash
sudo ln -s /etc/nginx/sites-available/module-guide /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d yourdomain.com
```

4. **Start production containers** (same as Option A):

```bash
docker-compose -f docker-compose.production.yml --env-file .env.production up -d --build
```

---

## Production vs Development

| Feature | Development | Production |
|---------|-------------|-----------|
| **Frontend Server** | Vite dev server (port 5173) | Built static files served by Flask |
| **Hot Reload** | ✅ Enabled | ❌ Disabled |
| **Source Maps** | ✅ Enabled | ❌ Disabled (minified) |
| **Compression** | ❌ No | ✅ Gzip enabled |
| **Caching** | ❌ No cache | ✅ Long-term cache for assets |
| **Debug Mode** | ✅ `DEBUG=True` | ❌ `DEBUG=False` |
| **CORS** | `localhost`, `127.0.0.1`, `frontend:5173` | Your production domain only |
| **Logging** | Console + file (DEBUG level) | File only (INFO level) |
| **Docker Compose** | `docker-compose.yml` | `docker-compose.production.yml` |

---

## Monitoring and Maintenance

### Health Checks

```bash
# API health
curl https://yourdomain.com/api/health

# Database health
curl https://yourdomain.com/api/health/db
```

### View Logs

```bash
# Application logs
docker-compose -f docker-compose.production.yml logs -f app

# Database logs
docker-compose -f docker-compose.production.yml logs -f db

# Flask logs (inside container)
docker exec -it module_guide_app_prod cat /app/logs/app.log
docker exec -it module_guide_app_prod cat /app/logs/errors.log
```

### Database Backup

```bash
# Backup database
docker exec module_guide_db_prod pg_dump -U module_guide module_guide > backup_$(date +%Y%m%d).sql

# Restore database
docker exec -i module_guide_db_prod psql -U module_guide module_guide < backup_20250101.sql
```

### Update Deployment

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart (zero-downtime with nginx)
docker-compose -f docker-compose.production.yml --env-file .env.production up -d --build

# Or with downtime (stops old containers first)
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml --env-file .env.production up -d --build
```

### Cleanup

```bash
# Remove unused Docker images (save disk space)
docker image prune -a

# Remove old containers
docker-compose -f docker-compose.production.yml down --volumes
```

---

## Troubleshooting

### Issue: Frontend Shows 404 Not Found

**Symptom**: Visiting `http://yourdomain.com/` returns 404 or error message.

**Causes**:
1. Flask is in debug mode (should be `FLASK_ENV=production`)
2. Static folder `/app/dist` doesn't exist in container

**Solution**:
```bash
# Check if dist folder exists in container
docker exec -it module_guide_app_prod ls -la /app/dist

# Rebuild with fresh build (no cache)
docker-compose -f docker-compose.production.yml build --no-cache app
docker-compose -f docker-compose.production.yml up -d app
```

### Issue: API Endpoints Return 404

**Symptom**: API calls like `/api/health` return 404.

**Cause**: Frontend SPA routing is catching API routes.

**Solution**: API routes are registered before the catch-all route, so this shouldn't happen. Check logs:
```bash
docker-compose -f docker-compose.production.yml logs app
```

### Issue: Static Assets Not Loading (404)

**Symptom**: HTML loads but JS/CSS files return 404.

**Cause**: Vite build uses relative paths, Flask can't find files.

**Solution**:
1. Check `frontend/vite.config.js` has correct `base` setting
2. Verify files exist: `docker exec -it module_guide_app_prod ls -la /app/dist/assets`

### Issue: Database Connection Failed

**Symptom**: `/api/health/db` returns error.

**Causes**:
1. Database container not running
2. Incorrect `DATABASE_URL`
3. Database not initialized

**Solution**:
```bash
# Check database is running
docker-compose -f docker-compose.production.yml ps

# Check database logs
docker-compose -f docker-compose.production.yml logs db

# Test database connection manually
docker exec -it module_guide_db_prod psql -U module_guide -d module_guide -c "SELECT 1;"
```

### Issue: Reviews Not Submitting (AI Errors)

**Symptom**: Review submission fails with 500 error.

**Cause**: Invalid or missing `GOOGLE_API_KEY`.

**Solution**:
```bash
# Check if API key is set
docker exec -it module_guide_app_prod printenv | grep GOOGLE_API_KEY

# Update .env.production and restart
nano .env.production
docker-compose -f docker-compose.production.yml restart app
```

### Issue: High Memory Usage

**Symptom**: Server running out of memory.

**Causes**:
1. Database connection pool too large
2. Too many concurrent requests

**Solution**:
```bash
# Reduce connection pool in .env.production
DB_POOL_MIN=1
DB_POOL_MAX=5

# Restart app
docker-compose -f docker-compose.production.yml restart app

# Monitor memory usage
docker stats
```

---

## Performance Optimization

### Enable HTTP/2 (Nginx)

Already enabled in the Nginx config above (`listen 443 ssl http2`).

### CDN for Static Assets

For better global performance, serve static assets from a CDN:

1. Build frontend locally: `cd frontend && npm run build`
2. Upload `dist/assets/*` to CDN (e.g., Cloudflare, AWS CloudFront)
3. Update `vite.config.js` to use CDN URL for `base`

### Database Query Optimization

- Connection pooling is already configured (`DB_POOL_MIN`, `DB_POOL_MAX`)
- Monitor slow queries: Check `logs/app.log` for database timing

### Rate Limiting

Already configured in `app.py`:
- **API calls**: 200/hour, 50/minute per IP
- **Review submission**: 5/hour per IP
- **Admin actions**: 100/hour per IP

---

## Security Checklist

- [ ] HTTPS enabled (SSL certificate via Let's Encrypt)
- [ ] `SECRET_KEY` is random and not committed to git
- [ ] `DB_PASSWORD` is strong and not default
- [ ] Database port (5432) is NOT exposed to public (only to app container)
- [ ] `CORS_ORIGINS` only includes your production domain
- [ ] Admin authentication implemented (see `CLAUDE-TODO.md` MYM-001)
- [ ] Regular database backups scheduled
- [ ] Firewall configured (only ports 80, 443, and SSH open)
- [ ] Docker containers run as non-root user (optional, advanced)
- [ ] Log monitoring and alerting set up

---

## Quick Reference

### Start Production

```bash
docker-compose -f docker-compose.production.yml --env-file .env.production up -d
```

### Stop Production

```bash
docker-compose -f docker-compose.production.yml down
```

### View Logs

```bash
docker-compose -f docker-compose.production.yml logs -f app
```

### Restart After Code Changes

```bash
git pull origin main
docker-compose -f docker-compose.production.yml up -d --build app
```

### Database Backup

```bash
docker exec module_guide_db_prod pg_dump -U module_guide module_guide > backup.sql
```

---

**Last Updated**: 2025-12-10
**Maintained By**: Meet Your Modules Development Team
