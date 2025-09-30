#!/usr/bin/env python3
"""
Fix Google Sheets headers for Property Maintenance Tracker
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def fix_spreadsheet_headers():
    """Fix the headers in the Google Spreadsheet"""
    try:
        # Set up credentials
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds_path = '/Users/eruzehaji/Desktop/PMT/credentials.json'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        gc = gspread.authorize(credentials)
        
        # Open spreadsheet
        spreadsheet = gc.open('Property Management Tracker')
        worksheet = spreadsheet.sheet1
        
        print("🔧 Fixing spreadsheet headers...")
        
        # Clear all content and start fresh
        worksheet.clear()
        
        # Add proper headers
        headers = [
            'Property',
            'Task Description', 
            'Due Date',
            'Priority',
            'Status',
            'Reporter Email',
            'Estimated Cost',
            'Actual Cost'
        ]
        
        worksheet.append_row(headers)
        print(f"✅ Added headers: {headers}")
        
        # Add some sample data for testing
        sample_tasks = [
            ['123 Main St', 'HVAC Filter Replacement', '2024-11-15', 'Medium', 'Pending', '', '75', ''],
            ['456 Oak Ave', 'Gutter Cleaning', '2024-11-20', 'High', 'Pending', '', '200', ''],
            ['789 Pine Rd', 'Smoke Detector Test', '2024-11-10', 'High', 'Completed', '', '50', '45']
        ]
        
        for task in sample_tasks:
            worksheet.append_row(task)
        
        print(f"✅ Added {len(sample_tasks)} sample tasks")
        
        # Verify the setup
        all_values = worksheet.get_all_values()
        print(f"📊 Spreadsheet now has {len(all_values)} rows (including header)")
        print(f"🔍 Headers: {all_values[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing headers: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Google Sheets headers...")
    print("=" * 50)
    
    success = fix_spreadsheet_headers()
    
    print("=" * 50)
    if success:
        print("🎉 Spreadsheet headers fixed successfully!")
        print("✅ Railway should now be able to work with the spreadsheet")
    else:
        print("❌ Failed to fix spreadsheet headers")