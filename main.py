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

# Also add src directory to path for imports
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main entry point for the web application."""
    try:
        # Import the FastAPI app
        from src.web.simple_main import app
        
        # Get port from environment variable (Render.com uses PORT)
        port = int(os.environ.get("PORT", 8000))
        host = os.environ.get("HOST", "0.0.0.0")
        
        print(f"🚀 Starting Postopus web server")
        print(f"📍 Host: {host}:{port}")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🐍 Python path: {sys.path[:3]}...")
        print(f"🌍 Environment: {os.environ.get('ENVIRONMENT', 'development')}")
        
        # Start the server
        uvicorn.run(
            app, 
            host=host, 
            port=port,
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"📁 Current working directory: {os.getcwd()}")
        print(f"🐍 Python path:")
        for i, path in enumerate(sys.path[:5]):
            print(f"  {i}: {path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()