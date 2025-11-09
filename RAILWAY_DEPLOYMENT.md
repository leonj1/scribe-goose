# 🚂 Railway Deployment Guide

This guide walks you through deploying the Audio Transcription Service to Railway.app.

## Overview

The application consists of three services:
1. **MySQL Database** - Managed by Railway
2. **Backend API (FastAPI)** - Python service
3. **Frontend (React)** - Web application

## Prerequisites

- Railway account (https://railway.app)
- Railway CLI installed (optional but recommended)
- GitHub repository with the code (already at: https://github.com/leonj1/scribe-goose)
- Google OAuth2 credentials (from Google Cloud Console)
- LLM API key (RequestYai or your provider)

---

## Step 1: Install Railway CLI (Optional)

```bash
# Using npm
npm install -g @railway/cli

# Or using Homebrew (macOS)
brew install railway

# Login to Railway
railway login
```

---

## Step 2: Create a New Railway Project

### Option A: Using Railway Dashboard

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `leonj1/scribe-goose`
5. Railway will detect the configuration automatically

### Option B: Using Railway CLI

```bash
# Navigate to project directory
cd /home/jose/src/scribe-bakeoff/goose

# Initialize Railway project
railway init

# Link to your GitHub repository
railway link
```

---

## Step 3: Add MySQL Database

### Using Railway Dashboard:

1. In your Railway project, click "+ New"
2. Select "Database"
3. Choose "Add MySQL"
4. Railway will provision a MySQL database and provide connection details

### Using Railway CLI:

```bash
railway add --database mysql
```

Railway will automatically create the `MYSQL_URL` environment variable.

---

## Step 4: Create Backend Service

### Using Railway Dashboard:

1. Click "+ New" in your project
2. Select "GitHub Repo"
3. Choose `leonj1/scribe-goose`
4. Railway will detect `backend/Dockerfile`
5. Set the **Root Directory** to `backend`
6. Service will be created

### Using Railway CLI:

```bash
# Create service from backend directory
railway up --service backend
```

---

## Step 5: Configure Backend Environment Variables

In the Railway dashboard, go to your **Backend Service** → **Variables** and add:

```bash
# Google OAuth2 Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://your-backend.railway.app/auth/google/callback

# LLM Provider
LLM_API_KEY=your-requestyai-api-key
LLM_PROVIDER=requestyai

# Database (automatically provided by Railway MySQL)
MYSQL_URL=${{MySQL.DATABASE_URL}}

# Security
JWT_SECRET=your-super-secret-jwt-key-at-least-32-characters-long

# Frontend URL (will be set after creating frontend)
FRONTEND_URL=https://your-frontend.railway.app

# CORS
CORS_ORIGINS=https://your-frontend.railway.app,http://localhost:3000

# Audio Storage
AUDIO_STORAGE_PATH=/app/audio_storage

# Server
PORT=8000
```

**Important Notes:**
- Replace `your-backend.railway.app` with your actual Railway backend domain
- Replace `your-frontend.railway.app` with your actual Railway frontend domain
- Use `${{MySQL.DATABASE_URL}}` to reference the Railway MySQL connection string
- Generate a strong JWT secret (use: `openssl rand -hex 32`)

---

## Step 6: Create Frontend Service

### Using Railway Dashboard:

1. Click "+ New" in your project
2. Select "GitHub Repo"
3. Choose `leonj1/scribe-goose`
4. Railway will detect `frontend/Dockerfile`
5. Set the **Root Directory** to `frontend`
6. Service will be created

### Using Railway CLI:

```bash
# Create service from frontend directory
railway up --service frontend
```

---

## Step 7: Configure Frontend Environment Variables

In the Railway dashboard, go to your **Frontend Service** → **Variables** and add:

```bash
# Backend API URL (from your backend service)
REACT_APP_API_URL=https://your-backend.railway.app

# Port (Railway provides this automatically)
PORT=3000
```

**Replace** `your-backend.railway.app` with your actual Railway backend domain.

---

## Step 8: Update Google OAuth2 Redirect URIs

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services** → **Credentials**
3. Select your OAuth 2.0 Client ID
4. Under **Authorized redirect URIs**, add:
   ```
   https://your-backend.railway.app/auth/google/callback
   ```
5. Under **Authorized JavaScript origins**, add:
   ```
   https://your-frontend.railway.app
   https://your-backend.railway.app
   ```
6. Click **Save**

---

## Step 9: Deploy Services

Railway will automatically deploy when you push to GitHub. To manually trigger:

### Using Railway Dashboard:
- Click "Deploy" on each service

### Using Railway CLI:
```bash
# Deploy all services
railway up

# Or deploy specific service
railway up --service backend
railway up --service frontend
```

---

## Step 10: Verify Deployment

### Check Service Status

1. Go to Railway dashboard
2. Verify all three services are running:
   - ✅ MySQL: Healthy
   - ✅ Backend: Healthy (check /health endpoint)
   - ✅ Frontend: Deployed

### Test Backend API

```bash
# Get your backend URL from Railway dashboard
BACKEND_URL=https://your-backend.railway.app

# Test health endpoint
curl $BACKEND_URL/health

# Expected response:
# {"status":"healthy"}

# Test API root
curl $BACKEND_URL/

# Expected response:
# {"name":"Audio Transcription Service","version":"1.0.0","status":"operational"}
```

### Test Frontend

Open your browser and navigate to:
```
https://your-frontend.railway.app
```

You should see the landing page with "Login with Google" button.

---

## Architecture on Railway

```
┌─────────────────────────────────────────────────────────┐
│                    Railway Project                       │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   MySQL      │  │   Backend    │  │   Frontend   │ │
│  │   Database   │◄─┤   (FastAPI)  │◄─┤   (React)    │ │
│  │              │  │              │  │              │ │
│  │  Port: 3306  │  │  Port: 8000  │  │  Port: 3000  │ │
│  │              │  │              │  │              │ │
│  │  Internal    │  │  Public URL  │  │  Public URL  │ │
│  │  Network     │  │  + Domain    │  │  + Domain    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                  │                  │         │
│         └──────────────────┴──────────────────┘         │
│                Private Network                           │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
                   Public Internet
                         │
                         ▼
               ┌─────────────────┐
               │  Healthcare     │
               │  Professionals  │
               └─────────────────┘
```

---

## Service Configuration Files

The project includes Railway-specific configuration files:

### Root Level
- `railway.json` - Basic project configuration
- `railway.toml` - Default service configuration

### Backend
- `backend/railway.toml` - Backend-specific configuration
- `backend/Dockerfile` - Backend container build

### Frontend
- `frontend/railway.toml` - Frontend-specific configuration
- `frontend/Dockerfile` - Frontend container build

---

## Environment Variables Reference

### Backend Service

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | `xxx.apps.googleusercontent.com` | ✅ Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Secret | `GOCSPX-xxx` | ✅ Yes |
| `GOOGLE_REDIRECT_URI` | OAuth callback URL | `https://api.railway.app/auth/callback` | ✅ Yes |
| `LLM_API_KEY` | LLM provider API key | `sk-xxx` | ✅ Yes |
| `LLM_PROVIDER` | LLM provider name | `requestyai` | ✅ Yes |
| `MYSQL_URL` | Database connection | `${{MySQL.DATABASE_URL}}` | ✅ Yes |
| `JWT_SECRET` | JWT signing secret | `random-32-char-string` | ✅ Yes |
| `FRONTEND_URL` | Frontend URL | `https://app.railway.app` | ✅ Yes |
| `CORS_ORIGINS` | Allowed CORS origins | `https://app.railway.app` | ✅ Yes |
| `AUDIO_STORAGE_PATH` | Audio file storage path | `/app/audio_storage` | ✅ Yes |
| `PORT` | Server port | `8000` | Auto-set |

### Frontend Service

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `REACT_APP_API_URL` | Backend API URL | `https://api.railway.app` | ✅ Yes |
| `PORT` | Server port | `3000` | Auto-set |

---

## Monitoring and Logs

### View Logs

#### Using Railway Dashboard:
1. Click on a service (Backend or Frontend)
2. Go to "Deployments" tab
3. Click on the latest deployment
4. View real-time logs

#### Using Railway CLI:
```bash
# View backend logs
railway logs --service backend

# View frontend logs
railway logs --service frontend

# Follow logs in real-time
railway logs --service backend --follow
```

### Health Checks

Railway automatically monitors the health of your services:

- **Backend**: Checks `/health` endpoint every 30 seconds
- **MySQL**: Checks MySQL port 3306
- **Frontend**: Checks HTTP response

---

## Scaling

### Vertical Scaling (Increase Resources)

1. Go to service in Railway dashboard
2. Click "Settings"
3. Adjust resource limits:
   - CPU
   - Memory
   - Disk

### Horizontal Scaling (Multiple Replicas)

Edit `railway.json`:
```json
{
  "deploy": {
    "numReplicas": 3
  }
}
```

**Note**: For database consistency, consider using Railway's managed MySQL with connection pooling.

---

## Custom Domains

### Add Custom Domain

1. Go to service in Railway dashboard
2. Click "Settings"
3. Scroll to "Domains"
4. Click "Add Domain"
5. Enter your custom domain (e.g., `api.yourdomain.com`)
6. Follow DNS configuration instructions

### SSL/TLS

Railway automatically provisions SSL certificates for all domains using Let's Encrypt.

---

## Database Management

### Access MySQL Database

#### Using Railway Dashboard:
1. Click on MySQL service
2. Go to "Connect" tab
3. Copy connection details

#### Using Railway CLI:
```bash
# Connect to database
railway connect MySQL
```

#### Using MySQL Client:
```bash
# Get connection string
railway variables --service MySQL

# Connect using mysql client
mysql -h [host] -P [port] -u [user] -p[password] [database]
```

### Backup Database

```bash
# Export database
railway run mysqldump -h ${{MySQL.MYSQL_HOST}} \
  -u ${{MySQL.MYSQL_USER}} \
  -p${{MySQL.MYSQL_PASSWORD}} \
  ${{MySQL.MYSQL_DATABASE}} > backup.sql

# Import database
railway run mysql -h ${{MySQL.MYSQL_HOST}} \
  -u ${{MySQL.MYSQL_USER}} \
  -p${{MySQL.MYSQL_PASSWORD}} \
  ${{MySQL.MYSQL_DATABASE}} < backup.sql
```

---

## Troubleshooting

### Backend Won't Start

1. **Check environment variables**: Ensure all required variables are set
2. **Check MySQL connection**: Verify `MYSQL_URL` is correct
3. **Check logs**: `railway logs --service backend`
4. **Common issues**:
   - Missing `JWT_SECRET`
   - Invalid `MYSQL_URL`
   - Missing `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`

### Frontend Can't Connect to Backend

1. **Check CORS**: Ensure `CORS_ORIGINS` includes frontend URL
2. **Check `REACT_APP_API_URL`**: Must point to backend URL
3. **Check backend health**: `curl https://your-backend.railway.app/health`
4. **Check browser console**: Look for CORS or network errors

### Database Connection Errors

1. **Check MySQL service**: Ensure it's running in Railway dashboard
2. **Check connection string**: Verify `MYSQL_URL` format
3. **Check network**: Backend and MySQL must be in same project
4. **Check credentials**: Verify username/password are correct

### Google OAuth Not Working

1. **Check redirect URI**: Must match Google Cloud Console configuration
2. **Check authorized origins**: Must include frontend and backend URLs
3. **Check credentials**: Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
4. **Check callback URL**: Should be `https://your-backend.railway.app/auth/google/callback`

---

## Security Best Practices

### Environment Variables

✅ **DO**:
- Store all secrets in Railway environment variables
- Use Railway's secret management
- Rotate JWT secrets regularly
- Use strong, random secrets

❌ **DON'T**:
- Commit `.env` files to Git
- Share secrets in plain text
- Use weak or default secrets
- Hardcode credentials in code

### Database

✅ **DO**:
- Use Railway's managed MySQL
- Enable automatic backups
- Use SSL/TLS connections
- Restrict database access to private network

❌ **DON'T**:
- Expose database publicly
- Use weak passwords
- Skip backups
- Allow root access

### HTTPS/TLS

✅ Railway automatically provides:
- Free SSL certificates
- Automatic certificate renewal
- HTTPS enforcement
- TLS 1.2+ support

---

## CI/CD with Railway

Railway automatically deploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin master

# Railway will automatically:
# 1. Detect the push
# 2. Build the Docker images
# 3. Run health checks
# 4. Deploy to production
```

### Deployment Workflow

```
┌─────────────┐
│  Git Push   │
│  to GitHub  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Railway   │
│  Webhook    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Build      │
│  Docker     │
│  Images     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Run Health │
│  Checks     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Deploy to  │
│  Production │
└─────────────┘
```

---

## Costs

Railway pricing (as of 2024):

- **Free Tier**: $5/month credit
  - Good for development/testing
  - Includes all services

- **Pro Plan**: $20/month + usage
  - Includes $5 credit
  - Pay for what you use
  - Production-ready

**Estimated Monthly Cost** (Production):
- MySQL Database: ~$5-10
- Backend Service: ~$10-15
- Frontend Service: ~$5-10
- **Total**: ~$20-35/month

---

## Support

### Railway Resources

- **Dashboard**: https://railway.app
- **Documentation**: https://docs.railway.app
- **Discord**: https://discord.gg/railway
- **Twitter**: [@Railway](https://twitter.com/Railway)

### Project Resources

- **GitHub**: https://github.com/leonj1/scribe-goose
- **Issues**: https://github.com/leonj1/scribe-goose/issues

---

## Quick Deployment Checklist

- [ ] Create Railway account
- [ ] Connect GitHub repository
- [ ] Add MySQL database service
- [ ] Create backend service
- [ ] Set backend environment variables
- [ ] Create frontend service
- [ ] Set frontend environment variables
- [ ] Configure Google OAuth redirect URIs
- [ ] Verify backend health endpoint
- [ ] Verify frontend loads
- [ ] Test Google login
- [ ] Test audio recording
- [ ] Test transcription
- [ ] Set up custom domain (optional)
- [ ] Configure monitoring
- [ ] Set up automated backups

---

## Conclusion

Your Audio Transcription Service is now deployed on Railway! 🚂✨

The application is:
- ✅ Production-ready
- ✅ Auto-scaling
- ✅ Monitored
- ✅ Secure (HTTPS)
- ✅ Backed up
- ✅ CI/CD enabled

For any issues, check the logs in Railway dashboard or refer to the troubleshooting section above.

Happy transcribing! 🩺🎙️
