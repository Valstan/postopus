#!/usr/bin/env python3
"""
Entry point for Postopus web application on Render.com
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app
from src.web.simple_main import app

if __name__ == "__main__":
    # Get port from environment variable (Render.com uses PORT)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Postopus web server")
    print(f"📍 Host: {host}:{port}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    
    # Start the server
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True
    )