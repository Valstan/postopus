#!/bin/bash
# start.sh - Production Startup Script for Render.com

set -o errexit

echo "🚀 Starting Postopus in production mode..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src"

# Check if database is available
echo "🔍 Checking database connection..."
python -c "
import asyncio
import sys
import os
sys.path.append('/opt/render/project/src')

async def check_db():
    try:
        from src.database.postgres import async_session
        if async_session:
            async with async_session() as session:
                await session.execute('SELECT 1')
            print('✅ Database connection successful')
            return True
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        print('🔄 Will use fallback demo data')
        return False

asyncio.run(check_db())
"

# Run database migrations if needed
echo "🗄️ Running database migrations..."
python -c "
import sys
sys.path.append('/opt/render/project/src')

try:
    from src.database.migrations import run_migrations
    run_migrations()
    print('✅ Migrations completed')
except Exception as e:
    print(f'⚠️ Migration skipped: {e}')
"

# Start the application
echo "🌟 Starting Postopus web server..."
exec gunicorn src.web.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info