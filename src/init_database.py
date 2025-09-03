#!/usr/bin/env python3
"""
Database initialization script for KYC system.
This script ensures the database exists and is properly configured.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager

def main():
    """Initialize the database."""
    print("🚀 KYC Database Initialization")
    print("=" * 50)
    
    try:
        # Get database information
        db_info = db_manager.get_database_info()
        
        print(f"📊 Database Path: {db_info.get('database_path', 'Unknown')}")
        print(f"📁 Database Exists: {db_info.get('database_exists', False)}")
        
        if db_info.get('database_exists'):
            print(f"📏 Database Size: {db_info.get('database_size_mb', 0)} MB")
            print(f"📋 Total Cases: {db_info.get('total_cases', 0)}")
            print(f"📄 Total Documents: {db_info.get('total_documents', 0)}")
            print(f"⚙️  Total Processing Steps: {db_info.get('total_processing_steps', 0)}")
        
        # Check database connection
        print("\n🔍 Testing database connection...")
        if db_manager.check_database_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return
        
        # Create tables if they don't exist
        print("\n🔧 Creating/verifying database tables...")
        db_manager.create_tables()
        print("✅ Database tables created/verified successfully")
        
        # Get updated database information
        updated_db_info = db_manager.get_database_info()
        
        print("\n📊 Final Database Status:")
        print(f"   Database Path: {updated_db_info.get('database_path')}")
        print(f"   Database Size: {updated_db_info.get('database_size_mb')} MB")
        print(f"   Total Cases: {updated_db_info.get('total_cases')}")
        print(f"   Total Documents: {updated_db_info.get('total_documents')}")
        print(f"   Total Processing Steps: {updated_db_info.get('total_processing_steps')}")
        
        print("\n" + "=" * 50)
        print("✅ Database initialization completed successfully!")
        print("\n🎯 Next steps:")
        print("1. Start the API server: python api_server.py")
        print("2. Start the admin dashboard: cd ../admin-dashboard && npm start")
        print("3. Start the customer portal: cd ../customer-portal && npm start")
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 