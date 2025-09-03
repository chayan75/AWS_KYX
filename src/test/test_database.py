#!/usr/bin/env python3
"""
Test script to check database connection and create tables.
"""

from database import db_manager
import os

def main():
    print("=== Database Test ===")
    
    # Check if database file exists
    db_file = "kyc_database.db"
    if os.path.exists(db_file):
        print(f"✅ Database file exists: {db_file}")
        print(f"📊 Database size: {os.path.getsize(db_file)} bytes")
    else:
        print(f"❌ Database file not found: {db_file}")
    
    try:
        # Create tables
        print("\n🔧 Creating database tables...")
        db_manager.create_tables()
        print("✅ Tables created successfully")
        
        # Test dashboard data
        print("\n📊 Testing dashboard data retrieval...")
        dashboard_data = db_manager.get_dashboard_data()
        print(f"✅ Dashboard data retrieved successfully")
        print(f"📈 Summary: {dashboard_data['summary']}")
        print(f"📋 Cases: {len(dashboard_data['cases'])} cases found")
        
        # Show sample cases if any exist
        if dashboard_data['cases']:
            print("\n📋 Sample cases:")
            for i, case in enumerate(dashboard_data['cases'][:3]):  # Show first 3 cases
                print(f"  {i+1}. {case['id']}: {case['name']} ({case['status']})")
        else:
            print("\n📋 No cases found in database")
            print("💡 Run the main.py script to process some KYC cases first")
        
        print("\n✅ Database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 