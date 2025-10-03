#!/usr/bin/env python3
"""
Simple web server startup - force web mode
"""
import os
import sys

# Ensure we have the right path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🌟 FORCING WEB SERVER MODE - NOT WORKER!")
print(f"Command args: {sys.argv}")
print(f"Working dir: {os.getcwd()}")

try:
    from src.web.main_render import app
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting web server on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)