#!/usr/bin/env python3
"""
Script to start the KYC Admin Dashboard API server using FastAPI.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def main():
    print("=== KYC Admin Dashboard Startup (FastAPI) ===")
    
    # Check if we're in the right directory
    if not Path("src/api_server.py").exists():
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    print("Starting FastAPI server...")
    print("API will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative Docs: http://localhost:8000/redoc")
    print("Health Check: http://localhost:8000/api/health")
    print("Admin dashboard should be available at: http://localhost:3000")
    print("\nTo start the admin dashboard frontend:")
    print("1. cd admin-dashboard")
    print("2. npm start")
    print("\nPress Ctrl+C to stop the API server")
    
    try:
        # Start the FastAPI server
        subprocess.run([sys.executable, "src/api_server.py"])
    except KeyboardInterrupt:
        print("\nFastAPI server stopped.")
    except Exception as e:
        print(f"Error starting FastAPI server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 