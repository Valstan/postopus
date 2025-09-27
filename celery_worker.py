#!/usr/bin/env python3
"""
Celery worker entry point for Postopus (separate from web application).
Only run this if you want to start Celery workers separately.
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Also add src directory to path
src_path = project_root / "src"  
sys.path.insert(0, str(src_path))

def main():
    """Start Celery worker."""
    try:
        print("🔧 Starting Celery worker for Postopus")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🐍 Python path: {sys.path[:3]}...")
        
        # Import Celery app
        from src.tasks.celery_app import celery_app
        
        # Start worker
        celery_app.worker_main(['worker', '--loglevel=info'])
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"📁 Current working directory: {os.getcwd()}")
        print(f"🐍 Python path:")
        for i, path in enumerate(sys.path[:5]):
            print(f"  {i}: {path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting Celery worker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()