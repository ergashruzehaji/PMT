#!/usr/bin/env python3
"""
Simple Google Sheets Uniform Formatter
Creates a professional, uniform table design matching the image
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def format_sheets_uniform():
    """Format Google Sheets to be uniform and professional"""
    
    print("🎨 Starting Google Sheets uniform formatting...")
    
    # Set up credentials
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json', scope)
    
    # Authorize and open spreadsheet
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open("Property Maintenance Tracker")
    
    # Get the main worksheet
    try:
        worksheet = spreadsheet.worksheet("Maintenance Tasks")
    except:
        worksheet = spreadsheet.sheet1
        # Rename it to "Maintenance Tasks"
        worksheet.update_title("Maintenance Tasks")
    
    print(f"📊 Working with worksheet: {worksheet.title}")
    
    # Define the uniform headers (matching the image structure)
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
    
    # Clear the first row and set headers
    print("📋 Setting uniform headers...")
    worksheet.delete_rows(1, 1)  # Clear first row
    worksheet.insert_row(headers, 1)  # Insert new headers
    
    # Format the header row to look professional
    print("🎯 Applying header formatting...")
    
    # Get all data to preserve existing entries
    try:
        all_data = worksheet.get_all_values()
        existing_data = all_data[1:]  # Skip header row
        print(f"📂 Found {len(existing_data)} existing data rows")
    except:
        existing_data = []
    
    # Clean and standardize existing data
    print("🧹 Standardizing existing data...")
    standardized_data = []
    
    for row in existing_data:
        # Ensure row has exactly 12 columns
        while len(row) < 12:
            row.append("")
        
        # Trim to exactly 12 columns
        row = row[:12]
        
        # Standardize certain fields
        if len(row) > 2 and row[2]:  # Category
            category = row[2].strip().title()
            if category not in ["General", "HVAC", "Plumbing", "Electrical", "Roofing", "Flooring", "Windows", "Appliances", "Exterior", "Landscaping", "Safety", "Other"]:
                row[2] = "General"
            else:
                row[2] = category
        
        if len(row) > 3 and row[3]:  # Priority
            priority = row[3].strip().title()
            if priority not in ["High", "Medium", "Low"]:
                row[3] = "Medium"
            else:
                row[3] = priority
        
        if len(row) > 4 and row[4]:  # Status
            status = row[4].strip().title()
            if status not in ["Pending", "In Progress", "Completed", "On Hold", "Cancelled"]:
                row[4] = "Pending"
            else:
                row[4] = status
        
        standardized_data.append(row)
    
    # Clear the worksheet and rebuild with uniform structure
    worksheet.clear()
    
    # Add headers back
    worksheet.insert_row(headers, 1)
    
    # Add standardized data
    if standardized_data:
        # Insert all data at once for efficiency
        worksheet.insert_rows(standardized_data, 2)
    
    print("✅ Uniform table structure applied!")
    print(f"📊 Headers: {', '.join(headers)}")
    print(f"📂 Data rows: {len(standardized_data)}")
    
    # Add some sample data if the sheet is mostly empty
    if len(standardized_data) < 3:
        print("📝 Adding sample data for demonstration...")
        sample_data = [
            ["123 Main St", "HVAC Filter Replacement", "HVAC", "Medium", "Pending", "2024-11-15", "2024-10-01", "", "75", "300", "Replace air filters in units 1-4", "maintenance@property.com"],
            ["456 Oak Ave", "Gutter Cleaning", "Exterior", "High", "Pending", "2024-11-20", "2024-10-01", "", "200", "800", "Clean gutters and downspouts", "manager@property.com"],
            ["789 Pine St", "Test task from Railway API", "General", "High", "Pending", "2024-12-01", "2024-10-01", "", "0", "0", "", ""],
            ["3678 42nd street", "Toilet leaks, new valves on every floor", "Plumbing", "High", "Pending", "2026-05-22", "", "", "", "", "", ""]
        ]
        
        worksheet.insert_rows(sample_data, len(standardized_data) + 2)
    
    print("🎉 Google Sheets uniform formatting complete!")
    print(f"🔗 Spreadsheet URL: {spreadsheet.url}")
    
    return True

if __name__ == "__main__":
    try:
        format_sheets_uniform()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure 'credentials.json' exists and you have access to the spreadsheet.")