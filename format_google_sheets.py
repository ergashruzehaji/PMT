#!/usr/bin/env python3
"""
Google Sheets Professional Formatting Script
Standardizes the Property Management Tracker sheet to match the professional table design
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import tempfile

class SheetsFormatter:
    def __init__(self, credentials_file_or_env, spreadsheet_name):
        """Initialize the Google Sheets formatter"""
        
        # Handle credentials from environment variable or file
        if credentials_file_or_env.startswith('{'):
            credentials_data = json.loads(credentials_file_or_env)
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                json.dump(credentials_data, f)
                credentials_file = f.name
        else:
            credentials_file = credentials_file_or_env
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(f"Credentials file not found: {credentials_file}")
        
        # Set up the credentials
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file, scope)
        
        # Authorize and open the spreadsheet
        self.gc = gspread.authorize(credentials)
        self.spreadsheet = self.gc.open(spreadsheet_name)
        
        # Get or create the main worksheet
        try:
            self.worksheet = self.spreadsheet.worksheet("Maintenance Tasks")
        except:
            # Create the worksheet if it doesn't exist
            self.worksheet = self.spreadsheet.add_worksheet(title="Maintenance Tasks", rows="1000", cols="20")
        
        # Clean up temporary file if created
        if credentials_file_or_env.startswith('{') and os.path.exists(credentials_file):
            os.unlink(credentials_file)
    
    def format_professional_table(self):
        """Apply professional table formatting to match the image design"""
        
        print("🎨 Applying professional table formatting...")
        
        # 1. Set up the headers with proper formatting
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
        
        # Clear existing content and set headers
        self.worksheet.clear()
        
        # Add headers in row 1
        header_range = f"A1:L1"
        self.worksheet.update(header_range, [headers])
        
        # 2. Format the header row (like Table1 style in the image)
        header_format = {
            "backgroundColor": {
                "red": 0.4,
                "green": 0.6,
                "blue": 0.4
            },
            "textFormat": {
                "foregroundColor": {
                    "red": 1.0,
                    "green": 1.0,
                    "blue": 1.0
                },
                "fontSize": 11,
                "bold": True
            },
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE"
        }
        
        # Apply header formatting
        self.worksheet.format(header_range, header_format)
        
        # 3. Set column widths for better readability
        column_widths = {
            "A": 180,  # Property Address
            "B": 250,  # Task Description
            "C": 120,  # Category
            "D": 100,  # Priority
            "E": 100,  # Status
            "F": 120,  # Due Date
            "G": 120,  # Created Date
            "H": 120,  # Completed Date
            "I": 120,  # Estimated Cost
            "J": 120,  # Emergency Cost
            "K": 200,  # Notes
            "L": 150   # Reporter Email
        }
        
        # Update column widths
        requests = []
        for col_letter, width in column_widths.items():
            col_index = ord(col_letter) - ord('A')
            requests.append({
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": col_index,
                        "endIndex": col_index + 1
                    },
                    "properties": {
                        "pixelSize": width
                    },
                    "fields": "pixelSize"
                }
            })
        
        # 4. Add borders and alternating row colors
        # This creates the professional table look
        data_format = {
            "borders": {
                "top": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}},
                "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}},
                "left": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}},
                "right": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}
            },
            "textFormat": {
                "fontSize": 10
            },
            "verticalAlignment": "MIDDLE"
        }
        
        # Apply formatting to data range (rows 2-100)
        data_range = "A2:L100"
        self.worksheet.format(data_range, data_format)
        
        # 5. Add alternating row colors for better readability
        even_row_format = {
            "backgroundColor": {
                "red": 0.98,
                "green": 0.98,
                "blue": 0.98
            }
        }
        
        # Apply to even rows (2, 4, 6, etc.)
        for row in range(2, 101, 2):
            even_range = f"A{row}:L{row}"
            self.worksheet.format(even_range, even_row_format)
        
        # 6. Execute the column width requests
        if requests:
            self.spreadsheet.batch_update({"requests": requests})
        
        # 7. Add sample data validation for specific columns
        self.add_data_validation()
        
        print("✅ Professional table formatting applied!")
        return True
    
    def add_data_validation(self):
        """Add dropdown data validation for consistent data entry"""
        
        print("📋 Adding data validation dropdowns...")
        
        # Category validation (Column C)
        category_values = [
            "General", "HVAC", "Plumbing", "Electrical", "Roofing", 
            "Flooring", "Windows", "Appliances", "Exterior", "Landscaping", 
            "Safety", "Other"
        ]
        
        # Priority validation (Column D)
        priority_values = ["High", "Medium", "Low"]
        
        # Status validation (Column E)
        status_values = ["Pending", "In Progress", "Completed", "On Hold", "Cancelled"]
        
        # Create validation requests
        validation_requests = [
            # Category validation
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "startRowIndex": 1,  # Row 2 (0-indexed)
                        "endRowIndex": 1000,
                        "startColumnIndex": 2,  # Column C
                        "endColumnIndex": 3
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [{"userEnteredValue": val} for val in category_values]
                        },
                        "showCustomUi": True,
                        "strict": True
                    }
                }
            },
            # Priority validation
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 3,  # Column D
                        "endColumnIndex": 4
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [{"userEnteredValue": val} for val in priority_values]
                        },
                        "showCustomUi": True,
                        "strict": True
                    }
                }
            },
            # Status validation
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 4,  # Column E
                        "endColumnIndex": 5
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [{"userEnteredValue": val} for val in status_values]
                        },
                        "showCustomUi": True,
                        "strict": True
                    }
                }
            }
        ]
        
        # Apply validation
        self.spreadsheet.batch_update({"requests": validation_requests})
        print("✅ Data validation dropdowns added!")
    
    def add_sample_data(self):
        """Add sample data to demonstrate the formatting"""
        
        print("📝 Adding sample data...")
        
        sample_data = [
            ["123 Main St", "HVAC Filter Replacement", "HVAC", "Medium", "Pending", "2024-11-15", "2024-10-01", "", "75", "300", "Replace air filters in units 1-4", "maintenance@property.com"],
            ["456 Oak Ave", "Gutter Cleaning", "Exterior", "High", "Pending", "2024-11-20", "2024-10-01", "", "200", "800", "Clean gutters and downspouts", "manager@property.com"],
            ["789 Pine St", "Toilet Leak Repair", "Plumbing", "High", "Completed", "2024-10-15", "2024-09-25", "2024-10-10", "150", "500", "Fixed leak in unit 2B bathroom", "tenant@email.com"],
            ["321 Elm Dr", "Window Seal Replacement", "Windows", "Medium", "In Progress", "2024-12-01", "2024-10-02", "", "300", "1200", "Replace worn weather sealing", "maintenance@property.com"]
        ]
        
        # Add sample data starting from row 2
        for i, row_data in enumerate(sample_data, 2):
            range_name = f"A{i}:L{i}"
            self.worksheet.update(range_name, [row_data])
        
        print("✅ Sample data added!")
    
    def apply_conditional_formatting(self):
        """Apply conditional formatting for status and priority visualization"""
        
        print("🎯 Applying conditional formatting...")
        
        # Priority color coding (Column D)
        priority_requests = [
            # High Priority - Red background
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": self.worksheet.id,
                            "startRowIndex": 1,
                            "endRowIndex": 1000,
                            "startColumnIndex": 3,
                            "endColumnIndex": 4
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": "High"}]
                            },
                            "format": {
                                "backgroundColor": {"red": 1.0, "green": 0.8, "blue": 0.8},
                                "textFormat": {"bold": True}
                            }
                        }
                    },
                    "index": 0
                }
            },
            # Medium Priority - Yellow background
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": self.worksheet.id,
                            "startRowIndex": 1,
                            "endRowIndex": 1000,
                            "startColumnIndex": 3,
                            "endColumnIndex": 4
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": "Medium"}]
                            },
                            "format": {
                                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.8}
                            }
                        }
                    },
                    "index": 1
                }
            },
            # Low Priority - Green background
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": self.worksheet.id,
                            "startRowIndex": 1,
                            "endRowIndex": 1000,
                            "startColumnIndex": 3,
                            "endColumnIndex": 4
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": "Low"}]
                            },
                            "format": {
                                "backgroundColor": {"red": 0.8, "green": 1.0, "blue": 0.8}
                            }
                        }
                    },
                    "index": 2
                }
            }
        ]
        
        # Status color coding (Column E)
        status_requests = [
            # Completed - Green background
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": self.worksheet.id,
                            "startRowIndex": 1,
                            "endRowIndex": 1000,
                            "startColumnIndex": 4,
                            "endColumnIndex": 5
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": "Completed"}]
                            },
                            "format": {
                                "backgroundColor": {"red": 0.7, "green": 1.0, "blue": 0.7},
                                "textFormat": {"bold": True}
                            }
                        }
                    },
                    "index": 3
                }
            },
            # In Progress - Blue background
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": self.worksheet.id,
                            "startRowIndex": 1,
                            "endRowIndex": 1000,
                            "startColumnIndex": 4,
                            "endColumnIndex": 5
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": "In Progress"}]
                            },
                            "format": {
                                "backgroundColor": {"red": 0.8, "green": 0.9, "blue": 1.0},
                                "textFormat": {"bold": True}
                            }
                        }
                    },
                    "index": 4
                }
            }
        ]
        
        # Apply all conditional formatting
        all_requests = priority_requests + status_requests
        self.spreadsheet.batch_update({"requests": all_requests})
        
        print("✅ Conditional formatting applied!")
    
    def freeze_header_row(self):
        """Freeze the header row for better navigation"""
        
        print("❄️ Freezing header row...")
        
        freeze_request = {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": self.worksheet.id,
                    "gridProperties": {
                        "frozenRowCount": 1
                    }
                },
                "fields": "gridProperties.frozenRowCount"
            }
        }
        
        self.spreadsheet.batch_update({"requests": [freeze_request]})
        print("✅ Header row frozen!")
    
    def format_complete_sheet(self, add_sample=False):
        """Apply complete professional formatting to the sheet"""
        
        print("\n🚀 Starting complete sheet formatting...")
        print("=" * 50)
        
        # Apply all formatting steps
        self.format_professional_table()
        self.add_data_validation()
        self.apply_conditional_formatting()
        self.freeze_header_row()
        
        if add_sample:
            self.add_sample_data()
        
        print("=" * 50)
        print("🎉 Complete professional formatting applied!")
        print(f"📊 Spreadsheet URL: {self.spreadsheet.url}")
        print("=" * 50)
        
        return True


def main():
    """Main function to run the formatting"""
    
    # Use local credentials file
    credentials_file = "credentials.json"
    spreadsheet_name = "Property Maintenance Tracker"
    
    if not os.path.exists(credentials_file):
        print("❌ Credentials file not found!")
        print("💡 Make sure 'credentials.json' exists in the project directory.")
        return
    
    try:
        formatter = SheetsFormatter(credentials_file, spreadsheet_name)
        
        # Apply complete formatting
        formatter.format_complete_sheet(add_sample=True)
        
        print("\n✨ Your Google Sheets is now professionally formatted!")
        print("🔗 Check your spreadsheet to see the new design.")
        
    except Exception as e:
        print(f"❌ Error formatting sheet: {e}")
        print("💡 Make sure your credentials are correct and you have access to the spreadsheet.")


if __name__ == "__main__":
    main()