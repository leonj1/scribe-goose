# Setup Guide - Audio Transcription Service

This guide provides detailed instructions for setting up and running the Audio Transcription Service.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Google OAuth Setup](#google-oauth-setup)
3. [LLM Provider Setup](#llm-provider-setup)
4. [Local Development](#local-development)
5. [Docker Setup](#docker-setup)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Docker** (version 20.10+) and **Docker Compose** (version 1.29+)
- **Node.js** (version 18+) and **npm** (for local development)
- **Python** (version 3.11+) and **pip** (for local development)
- **MySQL** (version 8.0+) (for local development without Docker)

### Required Accounts

- Google Cloud Platform account
- LLM provider account (RequestYai or similar)

## Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: "Audio Transcription Service"
4. Click "Create"

### Step 2: Enable Required APIs

1. Navigate to "APIs & Services" → "Library"
2. Search for "Google+ API" and enable it
3. Search for "Google Identity" and enable it

### Step 3: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: Audio Transcription Service
   - User support email: your email
   - Developer contact: your email
   - Scopes: email, profile, openid
   - Test users: add your email for testing
   - Click "Save and Continue"

4. Create OAuth Client ID:
   - Application type: Web application
   - Name: Audio Transcription Web Client
   - Authorized JavaScript origins:
     - `http://localhost:3000` (development)
     - `https://yourdomain.com` (production)
   - Authorized redirect URIs:
     - `http://localhost:8000/auth/google/callback` (development)
     - `https://api.yourdomain.com/auth/google/callback` (production)
   - Click "Create"

5. Copy the Client ID and Client Secret - you'll need these!

## LLM Provider Setup

### RequestYai Setup (Example)

1. Sign up at [RequestYai](https://requestyai.com/)
2. Navigate to API Settings
3. Generate a new API key
4. Note the API endpoint URL
5. Save both for your `.env` file

### Alternative Providers

If using a different LLM provider:
1. Create a new file: `backend/app/llm/your_provider.py`
2. Implement the `LLMProvider` interface
3. Update the configuration to use your provider

## Local Development

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor

# Set up MySQL database
mysql -u root -p
CREATE DATABASE audio_transcription;
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'apppassword';
GRANT ALL PRIVILEGES ON audio_transcription.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Run database migrations (if using Alembic)
alembic upgrade head

# Start the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env
nano .env
# Add: REACT_APP_API_URL=http://localhost:8000

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

## Docker Setup

### Step 1: Prepare Environment

```bash
# Create .env file in project root
cat > .env << EOF
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
JWT_SECRET=$(openssl rand -hex 32)
LLM_API_KEY=your-llm-api-key
LLM_API_URL=https://api.requestyai.com/v1/transcribe
ENCRYPTION_KEY=$(openssl rand -hex 32)
DEBUG=True
EOF
```

### Step 2: Build and Run

```bash
# Build all containers
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 3: Verify Installation

1. Check backend health:
   ```bash
   curl http://localhost:8000/health
   ```

2. Open frontend: http://localhost:3000

3. Try logging in with Google

### Step 4: Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Production Deployment

### Prerequisites

- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)
- Production-grade MySQL instance
- Cloud storage for audio files (S3, GCS, etc.)

### Step 1: Secure Configuration

```bash
# Generate secure secrets
export JWT_SECRET=$(openssl rand -hex 32)
export ENCRYPTION_KEY=$(openssl rand -hex 32)

# Create production .env
cat > .env.production << EOF
# Google OAuth (update redirect URIs in Google Console)
GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-client-secret
GOOGLE_REDIRECT_URI=https://api.yourdomain.com/auth/google/callback

# Security
JWT_SECRET=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# Database (use managed service)
MYSQL_URL=mysql+pymysql://user:pass@db-host:3306/audio_transcription

# LLM Provider
LLM_API_KEY=your-production-api-key
LLM_API_URL=https://api.requestyai.com/v1/transcribe

# Storage (use cloud storage)
AUDIO_STORAGE_PATH=/mnt/encrypted-storage

# Application
DEBUG=False
CORS_ORIGINS=https://yourdomain.com
EOF
```

### Step 2: SSL/TLS Setup

#### Option A: Using Nginx as Reverse Proxy

```nginx
# /etc/nginx/sites-available/audio-transcription

# Frontend
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Backend API
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Step 3: Database Setup

For production, use a managed database service:

- **AWS RDS** for MySQL
- **Google Cloud SQL**
- **Azure Database for MySQL**

Configure automated backups, point-in-time recovery, and read replicas.

### Step 4: Deploy with Docker

```bash
# Build for production
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Monitor
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 5: Health Monitoring

Set up monitoring with:
- Application logs → CloudWatch, Stackdriver, or ELK
- Uptime monitoring → UptimeRobot, Pingdom
- Error tracking → Sentry
- APM → New Relic, DataDog

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Error**: `Can't connect to MySQL server`

**Solutions**:
```bash
# Check MySQL is running
docker-compose ps mysql

# Check MySQL logs
docker-compose logs mysql

# Verify connection string
echo $MYSQL_URL

# Test connection
mysql -h localhost -u appuser -p audio_transcription
```

#### 2. Google OAuth Redirect Mismatch

**Error**: `redirect_uri_mismatch`

**Solutions**:
1. Verify redirect URI in `.env` matches exactly what's in Google Console
2. Include protocol (http:// or https://)
3. No trailing slashes
4. Case-sensitive matching

#### 3. Audio Recording Not Working

**Error**: `NotAllowedError: Permission denied`

**Solutions**:
1. Use HTTPS (required for microphone access except on localhost)
2. Check browser permissions
3. Try a different browser
4. Check browser console for detailed errors

#### 4. Transcription Not Appearing

**Possible causes**:
1. LLM API key invalid
2. Audio file too large
3. Network timeout

**Debug**:
```bash
# Check backend logs
docker-compose logs backend | grep transcription

# Check LLM provider status
curl -H "Authorization: Bearer $LLM_API_KEY" $LLM_API_URL/health

# Verify audio file exists
docker-compose exec backend ls -la /app/audio_storage/
```

#### 5. CORS Errors

**Error**: `Access-Control-Allow-Origin`

**Solutions**:
1. Check `CORS_ORIGINS` in backend `.env`
2. Ensure frontend URL is included
3. Restart backend after changes
4. Clear browser cache

### Getting Help

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify environment variables: `docker-compose config`
3. Test individual services:
   ```bash
   # Test backend
   curl http://localhost:8000/health

   # Test database
   docker-compose exec mysql mysql -u appuser -p audio_transcription
   ```

## Security Checklist

Before going to production:

- [ ] Change all default passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable audit logging
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerts
- [ ] Conduct security audit
- [ ] Review HIPAA compliance requirements
- [ ] Sign BAA with service providers
- [ ] Document incident response plan

## Next Steps

After successful setup:

1. Test all features thoroughly
2. Set up automated backups
3. Configure monitoring
4. Create user documentation
5. Train users
6. Plan regular security updates

For additional support, refer to the main [README.md](README.md) or contact support.
