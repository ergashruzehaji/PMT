#!/usr/bin/env python3
"""
Test Google Sheets connection locally to debug Railway issues
"""
import json
import os
import sys

try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    print("✅ Google Sheets libraries imported successfully")
except ImportError as e:
    print(f"❌ Missing libraries: {e}")
    sys.exit(1)

def test_google_sheets():
    """Test Google Sheets connection"""
    try:
        # Check credentials file
        creds_path = '/Users/eruzehaji/Desktop/PMT/credentials.json'
        if not os.path.exists(creds_path):
            print(f"❌ Credentials file not found: {creds_path}")
            return False
        
        print("✅ Credentials file found")
        
        # Set up credentials
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        print("📝 Setting up Google Sheets credentials...")
        credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        gc = gspread.authorize(credentials)
        print("✅ Google Sheets client authorized")
        
        # Try to open the spreadsheet
        spreadsheet_name = 'Property Management Tracker'
        print(f"📋 Attempting to open spreadsheet: '{spreadsheet_name}'")
        
        try:
            spreadsheet = gc.open(spreadsheet_name)
            worksheet = spreadsheet.sheet1
            print("✅ Spreadsheet opened successfully")
            
            # Check if it has data
            try:
                all_values = worksheet.get_all_values()
                print(f"📊 Spreadsheet has {len(all_values)} rows")
                
                if all_values:
                    print("🔍 First row (headers):")
                    print(all_values[0])
                    
                    # Check if headers are correct
                    expected_headers = ['Property', 'Task Description', 'Due Date', 'Priority', 'Status']
                    if len(all_values[0]) >= len(expected_headers):
                        headers_match = all(h in all_values[0][:len(expected_headers)] for h in expected_headers[:3])
                        if headers_match:
                            print("✅ Headers look good")
                        else:
                            print("⚠️ Headers might need adjustment")
                            print(f"Expected at least: {expected_headers[:3]}")
                            print(f"Found: {all_values[0][:5]}")
                    
                    # Try to add a test row
                    print("🧪 Testing write access...")
                    test_row = ['Test Property', 'Test Task', '2024-12-01', 'Medium', 'Pending']
                    worksheet.append_row(test_row)
                    print("✅ Successfully added test row")
                    
                    # Get updated data
                    updated_values = worksheet.get_all_values()
                    print(f"📊 Spreadsheet now has {len(updated_values)} rows")
                    
                    return True
                else:
                    print("⚠️ Spreadsheet is empty - need to add headers")
                    # Add headers
                    headers = ['Property', 'Task Description', 'Due Date', 'Priority', 'Status', 'Reporter Email', 'Estimated Cost', 'Actual Cost']
                    worksheet.append_row(headers)
                    print("✅ Added headers to spreadsheet")
                    return True
                    
            except Exception as e:
                print(f"❌ Error reading/writing spreadsheet data: {e}")
                return False
                
        except gspread.SpreadsheetNotFound:
            print(f"❌ Spreadsheet '{spreadsheet_name}' not found")
            print("📝 Please create a spreadsheet with this exact name and share it with:")
            print("   property-maintenance-service@property-maintenance-tracker.iam.gserviceaccount.com")
            return False
            
    except Exception as e:
        print(f"❌ Google Sheets connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Google Sheets Connection...")
    print("=" * 50)
    
    success = test_google_sheets()
    
    print("=" * 50)
    if success:
        print("🎉 Google Sheets connection test PASSED")
        print("✅ Railway should be able to connect to Google Sheets")
    else:
        print("❌ Google Sheets connection test FAILED")
        print("🔧 Please fix the issues above before testing Railway")