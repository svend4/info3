#!/usr/bin/env python3
"""
Simple HTTP Server for Frontend Dashboard
==========================================
Serves static files from current directory on port 8080.

Usage:
    python3 serve.py

Then open: http://localhost:8080
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 8080
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with CORS support"""

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.end_headers()

def main():
    """Start the HTTP server"""
    os.chdir(DIRECTORY)

    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 70)
        print("  RAG Knowledge Base Dashboard - Frontend Server")
        print("=" * 70)
        print(f"\n  🚀 Server running at: http://localhost:{PORT}")
        print(f"  📁 Serving files from: {DIRECTORY}")
        print("\n  Backend services required:")
        print("     • Production API:  http://localhost:8000")
        print("     • WebSocket Server: ws://localhost:8001")
        print("\n  Press Ctrl+C to stop")
        print("=" * 70)
        print()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n  Server stopped.")
            sys.exit(0)

if __name__ == "__main__":
    main()
