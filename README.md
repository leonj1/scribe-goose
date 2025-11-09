# 🩺 Audio Transcription Service for Healthcare

A HIPAA-compliant platform for healthcare professionals to record and transcribe patient notes securely and efficiently.

## Features

- 🔐 **Google OAuth2 Authentication** - Secure login with Google accounts
- 🎙️ **Long Audio Recording** - Record hours of audio with automatic chunking
- 📝 **AI-Powered Transcription** - Automatic transcription via LLM provider
- 📊 **Dashboard Management** - View and manage all recordings
- 🎨 **Modern UI** - Built with React and Ant Design
- 🔒 **HIPAA Compliant** - Secure data storage and encryption
- 📱 **Responsive Design** - Works on desktop and mobile devices

## Tech Stack

### Frontend
- React 18
- Ant Design UI Framework
- React Router for navigation
- Axios for API communication
- HTML5 MediaRecorder API for audio recording

### Backend
- FastAPI (Python 3.11)
- SQLAlchemy ORM
- MySQL Database
- Google OAuth2 (authlib)
- JWT Authentication
- Repository Pattern for data access
- LLM Provider Abstraction

## Prerequisites

- Docker and Docker Compose
- Google OAuth2 credentials
- LLM API key (RequestYai or similar)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd audio-transcription-service
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Google OAuth2 Credentials
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# JWT Secret
JWT_SECRET=your-super-secret-jwt-key

# LLM Provider
LLM_API_KEY=your-llm-api-key
LLM_API_URL=https://api.requestyai.com/v1/transcribe

# Encryption
ENCRYPTION_KEY=your-encryption-key-for-data-at-rest

# Debug Mode
DEBUG=True
```

### 3. Set Up Google OAuth2

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://localhost:8000/auth/google/callback`
6. Copy Client ID and Client Secret to `.env` file

### 4. Start the Application

```bash
docker-compose up -d
```

This will start:
- MySQL database on port 3306
- Backend API on port 8000
- Frontend on port 3000

### 5. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your credentials

# Run database migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm start
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration and utilities
│   │   ├── models/         # SQLAlchemy models
│   │   ├── repositories/   # Data access layer
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   └── llm/            # LLM provider abstraction
│   ├── tests/              # Backend tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts
│   │   ├── services/       # API services
│   │   └── App.js
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Authentication
- `GET /auth/google/login` - Initiate Google OAuth2 login
- `GET /auth/google/callback` - Handle OAuth callback
- `POST /auth/logout` - Logout

### Recordings
- `POST /recordings/` - Create new recording
- `GET /recordings/` - List all recordings
- `GET /recordings/{id}` - Get specific recording
- `POST /recordings/{id}/chunks` - Upload audio chunk
- `PATCH /recordings/{id}/pause` - Pause recording
- `POST /recordings/{id}/finish` - Finish and transcribe
- `PATCH /recordings/{id}/notes` - Add/update notes
- `DELETE /recordings/{id}` - Delete recording

## Database Schema

### Users Table
- id (UUID)
- google_id (unique)
- email
- display_name
- avatar_url
- created_at
- updated_at

### Recordings Table
- id (UUID)
- user_id (FK)
- status (active/paused/ended)
- audio_file_path
- transcription_text
- notes
- llm_provider
- created_at
- updated_at

### Recording Chunks Table
- id (UUID)
- recording_id (FK)
- chunk_index
- audio_blob_path
- duration_seconds
- uploaded_at

## Security Features

- ✅ Google OAuth2 authentication
- ✅ JWT bearer token authorization
- ✅ HTTPS/TLS support (configure in production)
- ✅ Encrypted data at rest
- ✅ CORS configuration
- ✅ SQL injection prevention (ORM)
- ✅ Input validation

## HIPAA Compliance Considerations

This system is designed with HIPAA compliance in mind:

1. **Access Control** - User authentication via Google OAuth2
2. **Audit Logging** - All database operations are logged
3. **Data Encryption** - Encryption at rest and in transit
4. **Secure Storage** - Controlled access to audio files
5. **Session Management** - Secure JWT-based sessions

⚠️ **Note**: For production HIPAA compliance, you must:
- Use HTTPS/TLS for all connections
- Implement comprehensive audit logging
- Set up backup and disaster recovery
- Complete BAA agreements with service providers
- Conduct security risk assessments

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Deployment

### Railway Deployment (Recommended)

The easiest way to deploy this application is using Railway.app. We provide a complete Railway deployment guide:

📖 **[Railway Deployment Guide](RAILWAY_DEPLOYMENT.md)** - Complete step-by-step instructions

#### Quick Railway Deployment:

1. Create account at [Railway.app](https://railway.app)
2. Connect GitHub repository: `leonj1/scribe-goose`
3. Add MySQL database service
4. Create backend and frontend services
5. Configure environment variables
6. Deploy automatically with Git push

**Benefits**:
- ✅ One-click MySQL database
- ✅ Automatic SSL/TLS certificates
- ✅ Auto-scaling and monitoring
- ✅ CI/CD with GitHub integration
- ✅ Free tier available

### Production Considerations

1. **Environment Variables**: Use secure secret management
2. **HTTPS**: Configure SSL/TLS certificates (automatic with Railway)
3. **Database**: Use managed MySQL service with backups
4. **Storage**: Use encrypted cloud storage (S3, etc.)
5. **Monitoring**: Set up application monitoring and logging
6. **Scaling**: Use container orchestration or Railway's auto-scaling

### Docker Production Build

```bash
# Backend
docker build -t audio-transcription-backend:latest ./backend

# Frontend
docker build -t audio-transcription-frontend:latest ./frontend
```

### Alternative Deployment Options

- **Railway** (Recommended) - See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)
- **AWS** - Use ECS/Fargate for containers, RDS for MySQL
- **Google Cloud** - Use Cloud Run for containers, Cloud SQL for MySQL
- **Azure** - Use Container Instances, Azure Database for MySQL
- **DigitalOcean** - Use App Platform or Kubernetes

## Troubleshooting

### Database Connection Issues

```bash
# Check if MySQL is running
docker-compose ps

# View MySQL logs
docker-compose logs mysql

# Restart MySQL
docker-compose restart mysql
```

### Audio Recording Not Working

- Ensure browser has microphone permissions
- Use HTTPS in production (HTTP only works on localhost)
- Check browser console for errors

### OAuth Redirect Issues

- Verify redirect URI in Google Console matches exactly
- Check GOOGLE_REDIRECT_URI in environment variables
- Ensure cookies/sessions are enabled

## Future Enhancements

- [ ] Multi-speaker diarization
- [ ] Export transcriptions to PDF
- [ ] Real-time transcription streaming
- [ ] Mobile app (React Native)
- [ ] Voice commands
- [ ] Custom vocabulary/medical terms
- [ ] Integration with EMR systems

## License

[Your License Here]

## Support

For issues and questions, please contact [support email]

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.
