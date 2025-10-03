#!/bin/bash
# build.sh - Render.com Build Script

set -o errexit  # Exit on any error

echo "🚀 Starting Postopus build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencies installed successfully!"

# Run database migrations (if needed)
echo "🗄️ Preparing database migrations..."
# Note: Actual migration will run on first startup

# Create necessary directories
echo "📁 Creating application directories..."
mkdir -p logs
mkdir -p static
mkdir -p uploads

echo "🔧 Setting up environment..."
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src"

echo "✅ Build completed successfully!"
echo "🎉 Postopus is ready for deployment!"