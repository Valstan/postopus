#!/bin/bash

# Postopus Deployment Script
# This script deploys Postopus to a production environment

set -e  # Exit on any error

echo "🚀 Starting Postopus Deployment..."

# Configuration
ENVIRONMENT=${1:-production}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-""}
IMAGE_TAG=${2:-latest}

echo "📋 Deployment Configuration:"
echo "   Environment: $ENVIRONMENT"
echo "   Image Tag: $IMAGE_TAG"
echo "   Registry: ${DOCKER_REGISTRY:-"local"}"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    echo "❌ Error: Environment must be 'development', 'staging', or 'production'"
    exit 1
fi

# Check dependencies
echo "🔍 Checking dependencies..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p temp_images
mkdir -p scripts
mkdir -p data/mongo
mkdir -p data/postgres
mkdir -p data/redis

# Environment-specific configuration
case $ENVIRONMENT in
    "development")
        COMPOSE_FILE="docker-compose.yml"
        echo "🔧 Using development configuration"
        ;;
    "staging")
        COMPOSE_FILE="docker-compose.staging.yml"
        echo "🔧 Using staging configuration"
        ;;
    "production")
        COMPOSE_FILE="docker-compose.prod.yml"
        echo "🔧 Using production configuration"
        ;;
esac

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
        echo "📝 Please edit .env file with your configuration before continuing"
        read -p "Press Enter to continue after editing .env file..."
    else
        echo "❌ Error: .env.example not found. Please create .env file manually."
        exit 1
    fi
fi

# Pull latest images (if using registry)
if [ -n "$DOCKER_REGISTRY" ]; then
    echo "📥 Pulling latest images..."
    docker-compose -f $COMPOSE_FILE pull
fi

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose -f $COMPOSE_FILE up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
services=("web" "mongo" "redis")

for service in "${services[@]}"; do
    if docker-compose -f $COMPOSE_FILE ps $service | grep -q "Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service failed to start"
        docker-compose -f $COMPOSE_FILE logs $service
        exit 1
    fi
done

# Database initialization
echo "🗄️  Initializing database..."
# Run migrations if needed
# docker-compose -f $COMPOSE_FILE exec web python -m alembic upgrade head

# Display service URLs
echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Service URLs:"
echo "   Web Interface: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Flower (Celery): http://localhost:5555"
echo "   MongoDB: localhost:27017"
echo "   PostgreSQL: localhost:5432"
echo "   Redis: localhost:6379"
echo ""
echo "📝 Useful commands:"
echo "   View logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "   Stop services: docker-compose -f $COMPOSE_FILE down"
echo "   Restart service: docker-compose -f $COMPOSE_FILE restart <service>"
echo "   Access shell: docker-compose -f $COMPOSE_FILE exec web bash"
echo ""
echo "✅ Postopus is now running!"