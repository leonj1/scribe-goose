#!/bin/bash

# Quick Start Script for Audio Transcription Service
# This script helps you get started quickly

set -e

echo "🩺 Audio Transcription Service - Quick Start"
echo "=============================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."

    # Generate secure secrets
    JWT_SECRET=$(openssl rand -hex 32)
    ENCRYPTION_KEY=$(openssl rand -hex 32)

    cat > .env << EOF
# Google OAuth2 Credentials
# IMPORTANT: Get these from https://console.cloud.google.com/
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# JWT Secret (auto-generated)
JWT_SECRET=${JWT_SECRET}

# LLM Provider
# IMPORTANT: Get your API key from your LLM provider
LLM_API_KEY=your-llm-api-key-here
LLM_API_URL=https://api.requestyai.com/v1/transcribe

# Encryption (auto-generated)
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# Debug Mode
DEBUG=True
EOF

    echo "✅ Created .env file with auto-generated secrets"
    echo ""
    echo "⚠️  IMPORTANT: You still need to configure:"
    echo "   1. GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"
    echo "      Get these from: https://console.cloud.google.com/"
    echo "   2. LLM_API_KEY"
    echo "      Get this from your LLM provider"
    echo ""
    echo "Edit .env file now? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        ${EDITOR:-nano} .env
    else
        echo ""
        echo "⏭️  Skipping .env editing for now"
        echo "   Remember to edit .env before starting the application!"
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🚀 Starting services with Docker Compose..."
echo ""

# Build and start containers
docker-compose build
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Services are up and running!"
    echo ""
    echo "📍 Access points:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "📝 Next Steps:"
    echo "   1. Ensure you've configured Google OAuth credentials in .env"
    echo "   2. Ensure you've configured LLM API key in .env"
    echo "   3. If you made changes to .env, restart with: docker-compose restart"
    echo "   4. Open http://localhost:3000 in your browser"
    echo ""
    echo "📚 Useful Commands:"
    echo "   View logs:        docker-compose logs -f"
    echo "   Stop services:    docker-compose down"
    echo "   Restart services: docker-compose restart"
    echo "   View status:      docker-compose ps"
    echo ""
    echo "🎉 Setup complete! Happy transcribing!"
else
    echo ""
    echo "❌ Some services failed to start"
    echo ""
    echo "View logs with: docker-compose logs"
    echo ""
    exit 1
fi
