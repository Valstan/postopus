#!/usr/bin/env python3
"""
Simple HTTP server for Celery workers to satisfy Render's port binding requirement.
This allows Celery workers to run as Web Services on Render's free plan.
"""

import os
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "service": "celery-worker"}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def start_health_server(port=8000):
    """Start a simple HTTP server for health checks"""
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f"Health check server started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Failed to start health server: {e}")

def main():
    """Main function to start Celery worker with health server"""
    if len(sys.argv) < 2:
        print("Usage: python worker_server.py <celery_command>")
        sys.exit(1)
    
    # Get port from environment variable
    port = int(os.environ.get('PORT', 8000))
    
    # Start health server in background thread
    health_thread = threading.Thread(target=start_health_server, args=(port,), daemon=True)
    health_thread.start()
    
    # Give health server time to start
    time.sleep(1)
    
    # Start Celery worker
    celery_command = ' '.join(sys.argv[1:])
    print(f"Starting Celery worker: {celery_command}")
    
    # Execute Celery command
    os.system(celery_command)

if __name__ == '__main__':
    main()
