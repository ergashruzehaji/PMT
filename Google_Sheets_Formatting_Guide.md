# Google Sheets Uniform Formatting Guide
## Property Management Tracker Template

### Step 1: Copy the Template Data
1. Open the file: Google_Sheets_Template.csv (on your desktop)
2. Open it in a text editor or Excel
3. Copy ALL the content
4. Go to your Google Sheets
5. Select cell A1 and paste

### Step 2: Apply Professional Formatting

#### Header Row (Row 1):
- **Background Color**: #4285F4 (Google Blue) or #E8F0FE (Light Blue)
- **Text Color**: White (for dark blue) or Black (for light blue)
- **Font Weight**: Bold
- **Font Size**: 11pt
- **Text Alignment**: Center
- **Borders**: All borders, medium thickness

#### Data Rows (Row 2 and below):
- **Font**: Arial or Google Sans
- **Font Size**: 10pt
- **Text Alignment**: Left (except dates and costs)
- **Borders**: Light gray, thin borders
- **Alternating Row Colors**: 
  - Even rows: White (#FFFFFF)
  - Odd rows: Light gray (#F8F9FA)

#### Column-Specific Formatting:

**Property Address (Column A):**
- Width: 120px
- Format: Text

**Task Description (Column B):**
- Width: 200px
- Format: Text
- Wrap text: Enabled

**Category (Column C):**
- Width: 100px
- Format: Text
- Data Validation: HVAC, Exterior, Interior, Plumbing, Electrical, General

**Priority (Column D):**
- Width: 80px
- Format: Text
- Data Validation: High, Medium, Low
- Conditional Formatting:
  - High = Red background (#FF0000)
  - Medium = Yellow background (#FFFF00)
  - Low = Green background (#00FF00)

**Status (Column E):**
- Width: 100px
- Format: Text
- Data Validation: Pending, In Progress, Completed
- Conditional Formatting:
  - Pending = Orange background (#FFA500)
  - In Progress = Blue background (#0000FF)
  - Completed = Green background (#008000)

**Due Date (Column F):**
- Width: 100px
- Format: Date (MM/DD/YYYY)
- Text Alignment: Center

**Created Date (Column G):**
- Width: 100px
- Format: Date (MM/DD/YYYY)
- Text Alignment: Center

**Completed Date (Column H):**
- Width: 110px
- Format: Date (MM/DD/YYYY)
- Text Alignment: Center

**Estimated Cost (Column I):**
- Width: 120px
- Format: Currency ($)
- Text Alignment: Right

**Emergency Priority (Column J):**
- Width: 120px
- Format: Text
- Data Validation: Yes, No
- Conditional Formatting:
  - Yes = Red background (#FF0000)
  - No = White background

**Notes (Column K):**
- Width: 250px
- Format: Text
- Wrap text: Enabled

### Step 3: Quick Format Application

#### Option A - Manual Formatting:
1. Select header row (Row 1)
2. Apply header formatting (bold, background color, borders)
3. Select all data rows
4. Apply data formatting (borders, alternating colors)
5. Apply column-specific formatting one by one

#### Option B - Copy Formatting:
1. Use the template I created in Google_Sheets_Template.csv
2. Copy and paste it into a new Google Sheet
3. The basic structure will be there
4. Apply colors and validation as described above

### Step 4: Data Validation Setup

For Category column (C):
1. Select column C (data rows only)
2. Data → Data validation
3. Criteria: List of items
4. Items: HVAC, Exterior, Interior, Plumbing, Electrical, General

For Priority column (D):
1. Select column D (data rows only)
2. Data → Data validation
3. Criteria: List of items
4. Items: High, Medium, Low

For Status column (E):
1. Select column E (data rows only)
2. Data → Data validation
3. Criteria: List of items
4. Items: Pending, In Progress, Completed

For Emergency Priority column (J):
1. Select column J (data rows only)
2. Data → Data validation
3. Criteria: List of items
4. Items: Yes, No

### Step 5: Conditional Formatting

Priority Colors:
1. Select Priority column data
2. Format → Conditional formatting
3. Set conditions for High (red), Medium (yellow), Low (green)

Status Colors:
1. Select Status column data
2. Format → Conditional formatting
3. Set conditions for each status with appropriate colors

### Final Result:
Your Google Sheet will have:
✅ Professional uniform appearance
✅ Consistent data entry with dropdowns
✅ Color-coded priorities and statuses
✅ Proper date and currency formatting
✅ Perfect compatibility with your app
✅ Easy data validation and error prevention

### Backup Plan:
If anything goes wrong:
1. Keep a backup copy of your current sheet
2. You can always revert to the original
3. The app will work with either format - this just makes it prettier and more professional

The template file is ready on your desktop: Google_Sheets_Template.csv