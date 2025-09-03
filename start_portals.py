#!/usr/bin/env python3
"""
Startup script to run both the admin dashboard and customer portal on different ports.
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

def run_command(command, cwd, name):
    """Run a command in a subprocess."""
    print(f"🚀 Starting {name}...")
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Start a thread to print output in real-time
        def print_output():
            try:
                for line in process.stdout:
                    print(f"[{name}] {line.rstrip()}")
            except Exception as e:
                print(f"[{name}] Error reading output: {e}")
        
        output_thread = threading.Thread(target=print_output, daemon=True)
        output_thread.start()
        
        return process
    except Exception as e:
        print(f"❌ Error starting {name}: {e}")
        return None

def check_port_available(port):
    """Check if a port is available."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def wait_for_port(port, timeout=30, name="Service"):
    """Wait for a port to become available."""
    import socket
    import time
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', port))
                print(f"✅ {name} is running on port {port}")
                return True
        except OSError:
            time.sleep(1)
    
    print(f"❌ {name} failed to start on port {port} within {timeout} seconds")
    return False

def main():
    """Main function to start both portals."""
    print("🎯 KYC Portal Startup Script")
    print("=" * 50)
    
    # Get the project root directory
    project_root = Path(__file__).parent
    admin_dashboard_dir = project_root / "admin-dashboard"
    customer_portal_dir = project_root / "customer-portal"
    src_dir = project_root / "src"
    
    # Check if directories exist
    if not admin_dashboard_dir.exists():
        print(f"❌ Admin dashboard directory not found: {admin_dashboard_dir}")
        return
    
    if not customer_portal_dir.exists():
        print(f"❌ Customer portal directory not found: {customer_portal_dir}")
        return
    
    if not src_dir.exists():
        print(f"❌ Source directory not found: {src_dir}")
        return
    
    # Check if ports are available
    if not check_port_available(3000):
        print("❌ Port 3000 is already in use (Admin Dashboard)")
        return
    
    if not check_port_available(3001):
        print("❌ Port 3001 is already in use (Customer Portal)")
        return
    
    processes = []
    
    try:
        # Initialize database first
        print("🔧 Initializing database...")
        init_process = subprocess.run(
            ["python", "init_database.py"],
            cwd=src_dir,
            capture_output=True,
            text=True
        )
        if init_process.returncode == 0:
            print("✅ Database initialization completed")
        else:
            print(f"❌ Database initialization failed: {init_process.stderr}")
            return
        
        # Start admin dashboard on port 3000
        print("\n📊 Starting Admin Dashboard on port 3000...")
        admin_process = run_command(
            "npm start",
            admin_dashboard_dir,
            "Admin Dashboard"
        )
        if admin_process:
            processes.append(("Admin Dashboard", admin_process, 3000))
        
        # Wait for admin dashboard to start
        if not wait_for_port(3000, timeout=60, name="Admin Dashboard"):
            print("❌ Admin Dashboard failed to start")
            return
        
        # Start customer portal on port 3001
        print("\n👤 Starting Customer Portal on port 3001...")
        customer_process = run_command(
            "npm start",
            customer_portal_dir,
            "Customer Portal"
        )
        if customer_process:
            processes.append(("Customer Portal", customer_process, 3001))
        
        # Wait for customer portal to start
        if not wait_for_port(3001, timeout=60, name="Customer Portal"):
            print("❌ Customer Portal failed to start")
            return
        
        print("\n" + "=" * 50)
        print("✅ All components are running successfully!")
        print("📊 Admin Dashboard: http://localhost:3000")
        print("👤 Customer Portal: http://localhost:3001")
        print("🔧 API Server: http://localhost:8000 (start separately)")
        print("\n💡 To start the API server, run: cd src && python api_server.py")
        print("\nPress Ctrl+C to stop all portals")
        print("=" * 50)
        
        # Keep the script running and monitor processes
        try:
            while True:
                # Check if any process has died
                for name, process, port in processes:
                    if process.poll() is not None:
                        print(f"❌ {name} has stopped unexpectedly")
                        return
                time.sleep(5)
        except KeyboardInterrupt:
            pass
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all portals...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up processes
        for name, process, port in processes:
            if process and process.poll() is None:
                print(f"🛑 Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        print("✅ All portals stopped")

if __name__ == "__main__":
    main() 