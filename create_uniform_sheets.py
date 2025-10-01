#!/usr/bin/env python3
"""
Google Sheets Uniform Formatter - Final Version
Creates the exact uniform table design matching your image
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials

def create_uniform_table():
    """Create a perfectly uniform Google Sheets table matching the image design"""
    
    print("🎨 Creating uniform Google Sheets table design...")
    
    # Connect to Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    gc = gspread.authorize(credentials)
    
    # Open the correct spreadsheet
    spreadsheet = gc.open("Property Management Tracker")
    worksheet = spreadsheet.sheet1
    
    print(f"📊 Working with: {spreadsheet.title}")
    print(f"🔗 URL: {spreadsheet.url}")
    
    # Get current data to preserve it
    try:
        current_data = worksheet.get_all_values()
        print(f"📂 Found {len(current_data)} existing rows")
        existing_data = current_data[1:] if len(current_data) > 1 else []  # Skip headers
    except:
        existing_data = []
    
    # Define the EXACT uniform headers matching your image
    uniform_headers = [
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
    
    print("🧹 Clearing and rebuilding sheet with uniform structure...")
    
    # Clear everything and start fresh
    worksheet.clear()
    
    # Add the uniform headers
    worksheet.append_row(uniform_headers)
    
    # Process and add existing data in uniform format
    uniform_data = []
    for row in existing_data:
        if not row or not any(row):  # Skip empty rows
            continue
            
        # Create a uniform row with exactly 12 columns
        uniform_row = [""] * 12
        
        # Map existing data to uniform format
        if len(row) > 0 and row[0]:  # Property Address
            uniform_row[0] = row[0].strip()
        
        if len(row) > 1 and row[1]:  # Task Description
            uniform_row[1] = row[1].strip()
        
        if len(row) > 2 and row[2]:  # Category
            category = row[2].strip().title()
            valid_categories = ["General", "HVAC", "Plumbing", "Electrical", "Roofing", "Flooring", "Windows", "Appliances", "Exterior", "Landscaping", "Safety", "Other"]
            uniform_row[2] = category if category in valid_categories else "General"
        else:
            uniform_row[2] = "General"
        
        if len(row) > 3 and row[3]:  # Priority
            priority = row[3].strip().title()
            valid_priorities = ["High", "Medium", "Low"]
            uniform_row[3] = priority if priority in valid_priorities else "Medium"
        else:
            uniform_row[3] = "Medium"
        
        if len(row) > 4 and row[4]:  # Status
            status = row[4].strip().title()
            valid_statuses = ["Pending", "In Progress", "Completed", "On Hold", "Cancelled"]
            uniform_row[4] = status if status in valid_statuses else "Pending"
        else:
            uniform_row[4] = "Pending"
        
        # Due Date (column 5 -> index 5)
        if len(row) > 5 and row[5]:
            uniform_row[5] = row[5].strip()
        
        # Created Date (column 6 -> index 6)
        if len(row) > 6 and row[6]:
            uniform_row[6] = row[6].strip()
        else:
            uniform_row[6] = "2024-10-01"  # Default created date
        
        # Completed Date (column 7 -> index 7)
        if len(row) > 7 and row[7]:
            uniform_row[7] = row[7].strip()
        
        # Estimated Cost (column 8 -> index 8)
        if len(row) > 8 and row[8]:
            cost = row[8].strip().replace('$', '').replace(',', '')
            uniform_row[8] = cost if cost.replace('.', '').isdigit() else "0"
        
        # Emergency Cost (column 9 -> index 9)
        if len(row) > 9 and row[9]:
            emergency_cost = row[9].strip().replace('$', '').replace(',', '')
            uniform_row[9] = emergency_cost if emergency_cost.replace('.', '').isdigit() else "0"
        
        # Notes (column 10 -> index 10)
        if len(row) > 10 and row[10]:
            uniform_row[10] = row[10].strip()
        
        # Reporter Email (column 11 -> index 11)
        if len(row) > 11 and row[11]:
            uniform_row[11] = row[11].strip()
        
        uniform_data.append(uniform_row)
    
    # Add all uniform data at once
    if uniform_data:
        worksheet.append_rows(uniform_data)
        print(f"✅ Added {len(uniform_data)} rows in uniform format")
    
    # Add sample data if sheet is mostly empty
    if len(uniform_data) < 2:
        print("📝 Adding sample data to demonstrate the uniform format...")
        sample_data = [
            ["123 Main St", "HVAC Filter Replacement", "HVAC", "Medium", "Pending", "2024-11-15", "2024-10-01", "", "75", "300", "Replace air filters in units 1-4", "maintenance@property.com"],
            ["456 Oak Ave", "Gutter Cleaning", "Exterior", "High", "Pending", "2024-11-20", "2024-10-01", "", "200", "800", "Clean gutters and downspouts", "manager@property.com"],
            ["Test Railway Property", "Test task from Railway API", "General", "High", "Pending", "2024-12-01", "2024-10-01", "", "0", "0", "", ""],
            ["3678 42nd street", "Toilet leaks, new valves on every floor", "Plumbing", "High", "Pending", "2026-05-22", "", "", "", "", "", ""]
        ]
        worksheet.append_rows(sample_data)
        print(f"✅ Added {len(sample_data)} sample rows")
    
    # Verify the final structure
    final_data = worksheet.get_all_values()
    print(f"\n📊 Final uniform sheet structure:")
    print(f"   📋 Headers: {final_data[0]}")
    print(f"   📂 Data rows: {len(final_data) - 1}")
    print(f"   🔗 Spreadsheet URL: {spreadsheet.url}")
    
    print("\n🎉 Google Sheets is now in perfect uniform format!")
    print("✨ All columns are standardized and match the design from your image")
    
    return True

if __name__ == "__main__":
    try:
        create_uniform_table()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()