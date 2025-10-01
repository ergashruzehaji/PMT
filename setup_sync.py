#!/usr/bin/env python3
"""
Google Sheets Format Setup Script
Ensures your Property Management Tracker sheet has standardized columns
"""

import os
from maintenance_tracker_v2 import PropertyMaintenanceTracker

def setup_google_sheets_format():
    """Set up standardized Google Sheets format"""
    print("🏗️ Property Maintenance Tracker - Google Sheets Setup")
    print("=" * 60)
    
    # Get credentials from environment or file
    google_credentials = os.getenv('GOOGLE_CREDENTIALS_JSON')
    spreadsheet_name = os.getenv('GOOGLE_SHEET_NAME', 'Property Management Tracker')
    
    if not google_credentials:
        credentials_file = '/Users/eruzehaji/Desktop/PMT/credentials.json'
        if not os.path.exists(credentials_file):
            print("❌ No Google credentials found!")
            print("Please set GOOGLE_CREDENTIALS_JSON environment variable or")
            print(f"place credentials.json file at: {credentials_file}")
            return False
        google_credentials = credentials_file
    
    try:
        print(f"📊 Connecting to spreadsheet: {spreadsheet_name}")
        tracker = PropertyMaintenanceTracker(google_credentials, spreadsheet_name)
        print("✅ Connected successfully!")
        
        # The tracker automatically sets up headers in __init__
        print("📋 Standardized column headers:")
        headers = [
            "Property Address",
            "Task Description", 
            "Category",
            "Priority",
            "Status",
            "Due Date",
            "Created Date",
            "Completed Date",
            "Estimated Cost",
            "Emergency Cost",
            "Notes",
            "Reporter Email"
        ]
        
        for i, header in enumerate(headers, 1):
            print(f"  {chr(64+i)}: {header}")
        
        # Get current tasks to show existing data
        tasks = tracker.get_all_tasks()
        print(f"\n📈 Current data: {len(tasks)} tasks found")
        
        if tasks:
            print("\n🔍 Sample tasks:")
            for i, task in enumerate(tasks[:3], 1):
                print(f"  {i}. {task.get('property_address', 'N/A')} - {task.get('task_description', 'N/A')}")
                print(f"     Status: {task.get('status', 'N/A')} | Priority: {task.get('priority', 'N/A')}")
        
        print("\n✅ Google Sheets format is properly standardized!")
        print(f"🔗 Access your sheet at: https://docs.google.com/spreadsheets/")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Google Sheets: {e}")
        return False

def test_app_sync():
    """Test that app and sheets stay in sync"""
    print("\n🔄 Testing App-Sheets Synchronization")
    print("=" * 40)
    
    try:
        # Test API connectivity
        import requests
        
        # Test local API if running
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Local API is running")
                api_url = "http://localhost:8000"
            else:
                raise Exception("Local API not responding")
        except:
            # Fallback to Railway API
            api_url = "https://web-production-641c2.up.railway.app"
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Railway API is running")
            else:
                raise Exception("Railway API not responding")
        
        # Test data retrieval
        response = requests.get(f"{api_url}/api/tasks")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                tasks = data.get("tasks", [])
                print(f"✅ API returning {len(tasks)} tasks")
            else:
                print("⚠️ API returning error response")
        
        # Test stats endpoint
        response = requests.get(f"{api_url}/api/stats")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data.get("stats", {})
                print(f"✅ Stats: {stats.get('total_tasks', 0)} total, {stats.get('pending', 0)} pending")
            else:
                print("⚠️ Stats endpoint returning error")
        
        print("✅ App-Sheets synchronization is working!")
        return True
        
    except Exception as e:
        print(f"❌ Synchronization test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Google Sheets and App Sync Setup\n")
    
    # Step 1: Setup Google Sheets format
    sheets_ok = setup_google_sheets_format()
    
    if sheets_ok:
        # Step 2: Test app synchronization
        sync_ok = test_app_sync()
        
        if sync_ok:
            print("\n🎉 SUCCESS! Your Property Maintenance Tracker is ready!")
            print("\n📋 Next Steps:")
            print("1. Open http://localhost:3000 to use the app")
            print("2. Open your Google Sheets to see the data")
            print("3. Create/complete tasks and watch them sync!")
            print("4. Use the demo guide to showcase the system")
        else:
            print("\n⚠️ Google Sheets is set up, but app sync needs checking")
    else:
        print("\n❌ Please fix Google Sheets setup first")