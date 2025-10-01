#!/usr/bin/env python3
"""
Expand Google Sheets to allow more rows for the Property Maintenance Tracker
"""

import sys
import os
sys.path.append('/Users/eruzehaji/Desktop/PMT')

from maintenance_tracker import PropertyMaintenanceTracker

def expand_google_sheets():
    try:
        # Initialize tracker
        tracker = PropertyMaintenanceTracker(
            '/Users/eruzehaji/Desktop/PMT/credentials.json', 
            'Property Management Tracker'
        )
        
        print("🔧 Expanding Google Sheets...")
        
        # Get current sheet info
        sheet = tracker.tasks_sheet
        current_rows = len(sheet.get_all_values())
        
        print(f"📊 Current rows: {current_rows}")
        print(f"🔧 Expanding to 100 rows...")
        
        # Resize the sheet to have more rows
        sheet.resize(rows=100, cols=11)
        
        print("✅ Google Sheets expanded successfully!")
        print("📋 You can now add up to 100 maintenance tasks")
        
        return True
        
    except Exception as e:
        print(f"❌ Error expanding sheets: {e}")
        return False

if __name__ == "__main__":
    success = expand_google_sheets()
    if success:
        print("\n🎉 Your Google Sheets is now ready for more tasks!")
    else:
        print("\n⚠️ Please manually expand your Google Sheets")