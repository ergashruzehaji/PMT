#!/usr/bin/env python3
"""
Debug Google Sheets content and fix the maintenance tracker
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def debug_and_fix_sheets():
    """Debug what's actually in the spreadsheet and fix it"""
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
        
        print("🔍 Current spreadsheet content:")
        print("-" * 40)
        
        # Get raw values
        all_values = worksheet.get_all_values()
        for i, row in enumerate(all_values):
            print(f"Row {i+1}: {row}")
        
        print("-" * 40)
        print(f"Total rows: {len(all_values)}")
        
        # Let's try updating specific cells instead of using append_row
        print("\n🔧 Setting headers using cell updates...")
        
        headers = ['Property', 'Task Description', 'Due Date', 'Priority', 'Status', 'Reporter Email', 'Estimated Cost', 'Actual Cost']
        
        # Clear the worksheet first
        worksheet.clear()
        
        # Set headers one by one
        for i, header in enumerate(headers, 1):
            worksheet.update_cell(1, i, header)
            print(f"Set cell (1,{i}) = '{header}'")
        
        # Add some test data
        test_data = [
            ['123 Main St', 'HVAC Filter Replacement', '2024-11-15', 'Medium', 'Pending', '', '75', ''],
            ['456 Oak Ave', 'Gutter Cleaning', '2024-11-20', 'High', 'Pending', '', '200', '']
        ]
        
        for row_num, data in enumerate(test_data, 2):  # Start at row 2
            for col_num, value in enumerate(data, 1):
                worksheet.update_cell(row_num, col_num, value)
        
        print(f"✅ Added {len(test_data)} test rows")
        
        # Read back the data
        print("\n📖 Reading back the data:")
        updated_values = worksheet.get_all_values()
        for i, row in enumerate(updated_values):
            print(f"Row {i+1}: {row}")
        
        # Test the maintenance tracker class
        print("\n🧪 Testing maintenance tracker...")
        from maintenance_tracker import PropertyMaintenanceTracker
        
        tracker = PropertyMaintenanceTracker(creds_path, 'Property Management Tracker')
        
        # Try to get all records
        records = tracker.tasks_sheet.get_all_records()
        print(f"📊 Found {len(records)} records:")
        for record in records:
            print(f"  {record}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Debugging Google Sheets content...")
    print("=" * 50)
    
    success = debug_and_fix_sheets()
    
    print("=" * 50)
    if success:
        print("🎉 Google Sheets debugging completed!")
    else:
        print("❌ Google Sheets debugging failed")