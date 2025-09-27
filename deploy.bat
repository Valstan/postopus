@echo off
REM Postopus Deployment Script for Windows
REM This script deploys Postopus to a development/production environment

echo 🚀 Starting Postopus Deployment...

REM Configuration
set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=development
set IMAGE_TAG=%2
if "%IMAGE_TAG%"=="" set IMAGE_TAG=latest

echo 📋 Deployment Configuration:
echo    Environment: %ENVIRONMENT%
echo    Image Tag: %IMAGE_TAG%

REM Validate environment
if not "%ENVIRONMENT%"=="development" if not "%ENVIRONMENT%"=="staging" if not "%ENVIRONMENT%"=="production" (
    echo ❌ Error: Environment must be 'development', 'staging', or 'production'
    exit /b 1
)

REM Check dependencies
echo 🔍 Checking dependencies...
docker --version >nul 2>&1 || (
    echo ❌ Docker is required but not installed. Please install Docker Desktop.
    exit /b 1
)

docker-compose --version >nul 2>&1 || (
    echo ❌ Docker Compose is required but not installed. Please install Docker Desktop.
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist logs mkdir logs
if not exist temp_images mkdir temp_images
if not exist scripts mkdir scripts
if not exist data mkdir data
if not exist data\mongo mkdir data\mongo
if not exist data\postgres mkdir data\postgres
if not exist data\redis mkdir data\redis

REM Environment-specific configuration
if "%ENVIRONMENT%"=="development" (
    set COMPOSE_FILE=docker-compose.yml
    echo 🔧 Using development configuration
) else if "%ENVIRONMENT%"=="staging" (
    set COMPOSE_FILE=docker-compose.staging.yml
    echo 🔧 Using staging configuration
) else if "%ENVIRONMENT%"=="production" (
    set COMPOSE_FILE=docker-compose.prod.yml
    echo 🔧 Using production configuration
)

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    if exist .env.example (
        copy .env.example .env
        echo ✅ Created .env from .env.example
        echo 📝 Please edit .env file with your configuration before continuing
        pause
    ) else (
        echo ❌ Error: .env.example not found. Please create .env file manually.
        exit /b 1
    )
)

REM Build and start services
echo 🏗️  Building and starting services...
docker-compose -f %COMPOSE_FILE% up --build -d

if errorlevel 1 (
    echo ❌ Failed to start services
    exit /b 1
)

REM Wait for services to be healthy
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Display service URLs
echo.
echo 🎉 Deployment completed successfully!
echo.
echo 📊 Service URLs:
echo    Web Interface: http://localhost:8000
echo    API Documentation: http://localhost:8000/docs
echo    Flower (Celery): http://localhost:5555
echo    MongoDB: localhost:27017
echo    PostgreSQL: localhost:5432
echo    Redis: localhost:6379
echo.
echo 📝 Useful commands:
echo    View logs: docker-compose -f %COMPOSE_FILE% logs -f
echo    Stop services: docker-compose -f %COMPOSE_FILE% down
echo    Restart service: docker-compose -f %COMPOSE_FILE% restart ^<service^>
echo    Access shell: docker-compose -f %COMPOSE_FILE% exec web bash
echo.
echo ✅ Postopus is now running!

pause