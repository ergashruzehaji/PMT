import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import tempfile
from datetime import datetime, date

class PropertyMaintenanceTracker:
    def __init__(self, credentials_file_or_env, spreadsheet_name):
        """
        Initialize tracker with standardized Google Sheets format
        
        Standard column format:
        A: Property Address
        B: Task Description  
        C: Category
        D: Priority
        E: Status
        F: Due Date
        G: Created Date
        H: Completed Date
        I: Estimated Cost
        J: Emergency Cost
        K: Notes
        L: Reporter Email
        """
        
        # Handle credentials from environment variable or file
        if credentials_file_or_env.startswith('{'):
            # It's JSON content from environment variable
            credentials_data = json.loads(credentials_file_or_env)
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                json.dump(credentials_data, f)
                credentials_file = f.name
        else:
            # It's a file path
            credentials_file = credentials_file_or_env
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(f"Credentials file not found: {credentials_file}")
        
        # Set up the credentials
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file, scope)
        
        # Authorize and open the spreadsheet
        gc = gspread.authorize(credentials)
        self.spreadsheet = gc.open(spreadsheet_name)
        
        # Try to get the worksheet - first try "Maintenance Tasks", then fall back to first sheet
        try:
            self.tasks_sheet = self.spreadsheet.worksheet("Maintenance Tasks")
        except:
            # Use the first worksheet (usually "Sheet1")
            self.tasks_sheet = self.spreadsheet.sheet1
        
        # Initialize headers if sheet is empty
        self._ensure_headers()
        
        # Clean up temporary file if created
        if credentials_file_or_env.startswith('{') and os.path.exists(credentials_file):
            os.unlink(credentials_file)
    
    def _ensure_headers(self):
        """Ensure the sheet has standardized headers"""
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
        
        # Check if first row has headers
        try:
            first_row = self.tasks_sheet.row_values(1)
            if not first_row or first_row[0] != "Property Address":
                # Set the headers
                for i, header in enumerate(headers, 1):
                    self.tasks_sheet.update_cell(1, i, header)
        except Exception:
            # If sheet is completely empty, add headers
            for i, header in enumerate(headers, 1):
                self.tasks_sheet.update_cell(1, i, header)
    
    def add_maintenance_task(self, property_address, task_description, 
                           due_date, priority="Medium", category="General", 
                           estimated_cost=0, emergency_cost=0, notes="", reporter_email=""):
        """Add a new maintenance task with standardized format"""
        # Get the next available row
        all_values = self.tasks_sheet.get_all_values()
        next_row = len(all_values) + 1
        
        # Prepare task data
        created_date = datetime.now().strftime('%Y-%m-%d')
        
        # Add the new task row by row to ensure proper formatting
        task_data = [
            property_address,           # A: Property Address
            task_description,           # B: Task Description
            category,                   # C: Category
            priority,                   # D: Priority
            "Pending",                  # E: Status
            due_date,                   # F: Due Date
            created_date,               # G: Created Date
            "",                         # H: Completed Date
            estimated_cost,             # I: Estimated Cost
            emergency_cost,             # J: Emergency Cost
            notes,                      # K: Notes
            reporter_email              # L: Reporter Email
        ]
        
        # Update each cell
        for col, value in enumerate(task_data, 1):
            self.tasks_sheet.update_cell(next_row, col, value)
        
        return {
            "success": True,
            "message": f"Task added: {task_description} for {property_address}",
            "row_number": next_row,
            "task_id": f"task_{next_row}"
        }
    
    def update_task_status(self, row_number, status, completed_date=None):
        """Update task status with proper date tracking"""
        # Update status (column E)
        self.tasks_sheet.update_cell(row_number, 5, status)
        
        # If marking as completed, add completion date
        if status.lower() == "completed" and not completed_date:
            completed_date = datetime.now().strftime('%Y-%m-%d')
        
        if completed_date:
            # Update completed date (column H)
            self.tasks_sheet.update_cell(row_number, 8, completed_date)
        
        return {
            "success": True,
            "message": f"Task in row {row_number} updated to {status}",
            "status": status,
            "completed_date": completed_date
        }
    
    def mark_task_complete_by_id(self, task_id_or_row):
        """Mark task complete by task ID or row number"""
        try:
            if isinstance(task_id_or_row, str) and task_id_or_row.startswith('task_'):
                row_number = int(task_id_or_row.split('_')[1])
            else:
                row_number = int(task_id_or_row)
            
            return self.update_task_status(row_number, "Completed")
        except (ValueError, IndexError):
            return {"success": False, "message": "Invalid task ID or row number"}
    
    def get_all_tasks(self):
        """Get all tasks in standardized format"""
        try:
            all_records = self.tasks_sheet.get_all_records()
            
            # Convert to standardized format for the app
            standardized_tasks = []
            for i, task in enumerate(all_records, 2):  # Start from row 2 (skip header)
                standardized_task = {
                    "id": f"task_{i}",
                    "row_number": i,
                    "property_address": task.get("Property Address", ""),
                    "property_name": task.get("Property Address", ""),  # Alias for compatibility
                    "task_description": task.get("Task Description", ""),
                    "task_name": task.get("Task Description", ""),  # Alias for compatibility
                    "category": task.get("Category", "General"),
                    "priority": task.get("Priority", "Medium"),
                    "status": task.get("Status", "Pending"),
                    "due_date": task.get("Due Date", ""),
                    "created_date": task.get("Created Date", ""),
                    "completed_date": task.get("Completed Date", ""),
                    "estimated_cost": self._parse_cost(task.get("Estimated Cost", 0)),
                    "emergency_cost": self._parse_cost(task.get("Emergency Cost", 0)),
                    "emergency_cost_if_delayed": self._parse_cost(task.get("Emergency Cost", 0)),  # Alias
                    "notes": task.get("Notes", ""),
                    "description": task.get("Notes", ""),  # Alias for compatibility
                    "reporter_email": task.get("Reporter Email", ""),
                    
                    # Add legacy format support for backward compatibility
                    "Property": task.get("Property Address", ""),
                    "Task Description": task.get("Task Description", ""),
                    "Category": task.get("Category", "General"),
                    "Priority": task.get("Priority", "Medium"),
                    "Status": task.get("Status", "Pending"),
                    "Due Date": task.get("Due Date", ""),
                    "Estimated Cost": self._parse_cost(task.get("Estimated Cost", 0)),
                    "Emergency Cost": self._parse_cost(task.get("Emergency Cost", 0))
                }
                standardized_tasks.append(standardized_task)
            
            return standardized_tasks
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []
    
    def _parse_cost(self, cost_value):
        """Parse cost value from various formats"""
        if isinstance(cost_value, (int, float)):
            return float(cost_value)
        if isinstance(cost_value, str):
            # Remove currency symbols and commas
            cleaned = cost_value.replace('$', '').replace(',', '').strip()
            try:
                return float(cleaned) if cleaned else 0.0
            except ValueError:
                return 0.0
        return 0.0
    
    def get_pending_tasks(self):
        """Get all pending maintenance tasks"""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.get('status', '').lower() == 'pending']
    
    def get_overdue_tasks(self):
        """Get overdue tasks for reminder emails"""
        all_tasks = self.get_all_tasks()
        overdue_tasks = []
        current_date = datetime.now().date()
        
        for task in all_tasks:
            if task.get('status', '').lower() == 'pending':
                try:
                    due_date_str = task.get('due_date', '')
                    if due_date_str:
                        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                        if due_date < current_date:
                            overdue_tasks.append(task)
                except ValueError:
                    continue  # Skip tasks with invalid date format
        
        return overdue_tasks
    
    def get_completed_tasks(self):
        """Get all completed tasks"""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.get('status', '').lower() == 'completed']
    
    def get_tasks_by_property(self, property_name):
        """Get all tasks for a specific property"""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if property_name.lower() in task.get('property_address', '').lower()]
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        all_tasks = self.get_all_tasks()
        
        total_tasks = len(all_tasks)
        pending_tasks = len([t for t in all_tasks if t.get('status', '').lower() == 'pending'])
        completed_tasks = len([t for t in all_tasks if t.get('status', '').lower() == 'completed'])
        overdue_tasks = len(self.get_overdue_tasks())
        
        # Calculate cost savings
        completed = self.get_completed_tasks()
        preventive_cost = sum(t.get('estimated_cost', 0) for t in completed)
        emergency_cost_averted = sum(t.get('emergency_cost', 0) for t in completed)
        
        # If emergency costs aren't specified, estimate as 6x preventive cost
        if emergency_cost_averted == 0 and preventive_cost > 0:
            emergency_cost_averted = preventive_cost * 6
        
        net_savings = emergency_cost_averted - preventive_cost
        
        return {
            "total_tasks": total_tasks,
            "pending": pending_tasks,
            "completed": completed_tasks,
            "overdue": overdue_tasks,
            "preventive_cost": preventive_cost,
            "emergency_cost_averted": emergency_cost_averted,
            "net_savings": net_savings
        }

    def add_task_from_api(self, task_data):
        """Add task from API with flexible field mapping"""
        return self.add_maintenance_task(
            property_address=task_data.get('property_name', task_data.get('property_address', '')),
            task_description=task_data.get('task_description', task_data.get('task_name', '')),
            due_date=task_data.get('due_date', ''),
            priority=task_data.get('priority', 'Medium'),
            category=task_data.get('category', 'General'),
            estimated_cost=task_data.get('estimated_cost', 0),
            emergency_cost=task_data.get('emergency_cost', task_data.get('emergency_cost_if_delayed', 0)),
            notes=task_data.get('notes', task_data.get('description', '')),
            reporter_email=task_data.get('reporter_email', '')
        )

# For backward compatibility
PropertyMaintenanceTrackerV2 = PropertyMaintenanceTracker