import gspread
from google.oauth2.service_account import Credentials
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyManagementTracker:
    """Property Management Tracker for PMT-Project spreadsheet"""
    
    def __init__(self, credentials_file: str, spreadsheet_name: str) -> None:
        """Initialize tracker with credentials and spreadsheet name"""
        if not os.path.exists(credentials_file):
            raise FileNotFoundError(
                f"Credentials file not found: {credentials_file}\n"
                "Please ensure you have:\n"
                "1. Created a Google Cloud Service Account\n"
                "2. Downloaded the JSON credentials file\n"
                "3. Placed it at the specified path\n"
                "4. Enabled Google Sheets and Google Drive APIs"
            )
        
        # Use google-auth instead of deprecated oauth2client
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        try:
            credentials = Credentials.from_service_account_file(
                credentials_file,
                scopes=scope
            )
            gc = gspread.authorize(credentials)
            
            # Open the spreadsheet by name (PMT-Project)
            self.spreadsheet = gc.open(spreadsheet_name)
            logger.info(f"Successfully opened spreadsheet: {spreadsheet_name}")
            
            # Try to get "Maintenance Tasks" worksheet, fall back to first sheet
            try:
                self.tasks_sheet = self.spreadsheet.worksheet("Maintenance Tasks")
                logger.info("Using 'Maintenance Tasks' worksheet")
            except gspread.WorksheetNotFound:
                self.tasks_sheet = self.spreadsheet.sheet1
                logger.warning("'Maintenance Tasks' worksheet not found, using first sheet")
                
        except gspread.SpreadsheetNotFound:
            raise ValueError(
                f"Spreadsheet '{spreadsheet_name}' not found.\n"
                f"Make sure:\n"
                f"1. The spreadsheet exists\n"
                f"2. It's named exactly 'PMT-Project'\n"
                f"3. You've shared it with your service account email"
            )
        except Exception as e:
            raise Exception(f"Failed to initialize tracker: {e}")
    
    def _format_date_for_sheet(self, date_str: str) -> str:
        """Convert date to MM-DD-YYYY format for Google Sheets"""
        if not date_str:
            return ''
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return "'" + date_obj.strftime('%m-%d-%Y')
        except ValueError:
            try:
                datetime.strptime(date_str, '%m-%d-%Y')
                return "'" + date_str
            except ValueError:
                logger.warning(f"Invalid date format: {date_str}")
                return date_str
    
    def _parse_date_from_sheet(self, date_str: str) -> str:
        """Convert date from sheet format to YYYY-MM-DD for API"""
        if not date_str:
            return ''
        
        date_str = str(date_str).lstrip("'")
        
        try:
            date_obj = datetime.strptime(date_str, '%m-%d-%Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                return date_str
    
    def _convert_to_float(self, value: Any) -> float:
        """Safely convert value to float"""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                clean_value = value.replace('$', '').replace(',', '').strip()
                return float(clean_value) if clean_value else 0.0
            except (ValueError, AttributeError):
                return 0.0
        return 0.0
    
    def add_maintenance_task(
        self, 
        property_name: str, 
        task_description: str,
        due_date: str, 
        priority: str = "Medium", 
        category: str = "General",
        estimated_cost: float = 0, 
        notes: str = "", 
        reporter_email: str = ""
    ) -> str:
        """Add a new maintenance task to the tracking sheet"""
        try:
            tasks = self.tasks_sheet.get_all_values()
            next_row = len(tasks) + 1
            
            formatted_date = self._format_date_for_sheet(due_date)
            
            # Update cells - matches PMT-Project spreadsheet column order
            self.tasks_sheet.update_cell(next_row, 1, property_name)
            self.tasks_sheet.update_cell(next_row, 2, task_description)
            self.tasks_sheet.update_cell(next_row, 3, category)
            self.tasks_sheet.update_cell(next_row, 4, priority)
            self.tasks_sheet.update_cell(next_row, 5, "Pending")
            self.tasks_sheet.update_cell(next_row, 6, formatted_date)
            self.tasks_sheet.update_cell(next_row, 8, str(estimated_cost))
            self.tasks_sheet.update_cell(next_row, 10, notes)
            self.tasks_sheet.update_cell(next_row, 11, reporter_email)
            
            logger.info(f"Added task: {task_description} for {property_name}")
            return f"Task added: {task_description} for {property_name}"
            
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            raise
    
    def add_task_from_api(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add task from API request"""
        try:
            result = self.add_maintenance_task(
                property_name=task_data.get('property_name', ''),
                task_description=task_data.get('task_description', ''),
                due_date=task_data.get('due_date', ''),
                priority=task_data.get('priority', 'Medium'),
                category=task_data.get('category', 'General'),
                estimated_cost=task_data.get('estimated_cost', 0),
                notes=task_data.get('notes', ''),
                reporter_email=task_data.get('reporter_email', '')
            )
            return {"success": True, "message": result}
        except Exception as e:
            logger.error(f"API task creation failed: {e}")
            return {"success": False, "message": f"Error adding task: {str(e)}"}
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks in standardized format"""
        try:
            all_records = self.tasks_sheet.get_all_records()
            
            normalized_tasks = []
            for i, record in enumerate(all_records, start=2):
                normalized_task = {
                    "id": f"task_{i}",
                    "row_number": i,
                    "property_name": record.get('Property Address', ''),
                    "property_address": record.get('Property Address', ''),
                    "task_description": record.get('Task Description', ''),
                    "task_name": record.get('Task Description', ''),
                    "category": record.get('Category', 'General'),
                    "priority": record.get('Priority', 'Medium'),
                    "status": record.get('Status', 'Pending'),
                    "due_date": self._parse_date_from_sheet(str(record.get('Due Date', ''))),
                    "completed_date": self._parse_date_from_sheet(str(record.get('Completed Date', ''))),
                    "estimated_cost": self._convert_to_float(record.get('Estimated Cost', 0)),
                    "emergency_cost": self._convert_to_float(record.get('Emergency Cost', 0)),
                    "notes": record.get('Notes', ''),
                    "description": record.get('Notes', ''),
                    "reporter_email": record.get('Reporter Email', ''),
                    "created_date": self._parse_date_from_sheet(str(record.get('Date Created', ''))),
                }
                normalized_tasks.append(normalized_task)
            
            return normalized_tasks
            
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []
    
    def update_task_status(
        self, 
        row_number: int, 
        status: str, 
        completed_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update task status and completion date"""
        try:
            self.tasks_sheet.update_cell(row_number, 5, status)
            
            if status.lower() == 'completed':
                if not completed_date:
                    completed_date = datetime.now().strftime('%Y-%m-%d')
                
                formatted_date = self._format_date_for_sheet(completed_date)
                self.tasks_sheet.update_cell(row_number, 7, formatted_date)
            
            logger.info(f"Updated task {row_number} to status: {status}")
            return {"success": True, "message": f"Task status updated to {status}"}
            
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            return {"success": False, "message": f"Failed to update task: {str(e)}"}
    
    def delete_task(self, row_number: int) -> Dict[str, Any]:
        """Delete a task by row number"""
        try:
            self.tasks_sheet.delete_rows(row_number)
            logger.info(f"Deleted task at row {row_number}")
            return {"success": True, "message": f"Task in row {row_number} deleted successfully"}
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            return {"success": False, "message": f"Failed to delete task: {str(e)}"}
    
    def mark_task_complete(self, row_number: int) -> str:
        """Mark a task as complete"""
        result = self.update_task_status(row_number, "Completed")
        if result["success"]:
            return f"Task in row {row_number} marked as complete"
        return result["message"]
    
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get all pending tasks"""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.get('status', '').lower() == 'pending']
    
    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Get all overdue tasks"""
        all_tasks = self.get_all_tasks()
        overdue_tasks = []
        today = datetime.now().date()
        
        for task in all_tasks:
            if task.get('status', '').lower() != 'completed':
                due_date_str = task.get('due_date', '')
                if due_date_str:
                    try:
                        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                        if due_date < today:
                            overdue_tasks.append(task)
                    except ValueError:
                        continue
        
        return overdue_tasks
    
    def get_tasks_by_property(self, property_name: str) -> List[Dict[str, Any]]:
        """Get all tasks for a specific property"""
        all_tasks = self.get_all_tasks()
        return [
            task for task in all_tasks 
            if task.get('property_name', '').lower() == property_name.lower()
        ]
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        try:
            all_tasks = self.get_all_tasks()
            
            total_tasks = len(all_tasks)
            pending_tasks = len([t for t in all_tasks if t.get('status', '').lower() == 'pending'])
            completed_tasks = len([t for t in all_tasks if t.get('status', '').lower() == 'completed'])
            
            overdue_tasks = self.get_overdue_tasks()
            overdue_count = len(overdue_tasks)
            
            preventive_cost = sum(
                t.get('estimated_cost', 0) 
                for t in all_tasks 
                if t.get('status', '').lower() == 'completed'
            )
            
            emergency_cost_averted = preventive_cost * 6.0
            net_savings = emergency_cost_averted - preventive_cost
            
            return {
                "total_tasks": total_tasks,
                "pending": pending_tasks,
                "overdue": overdue_count,
                "completed": completed_tasks,
                "preventive_cost": round(preventive_cost, 2),
                "emergency_cost_averted": round(emergency_cost_averted, 2),
                "net_savings": round(net_savings, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate stats: {e}")
            return {
                "total_tasks": 0,
                "pending": 0,
                "overdue": 0,
                "completed": 0,
                "preventive_cost": 0.0,
                "emergency_cost_averted": 0.0,
                "net_savings": 0.0
            }
    
    # Additional methods for compatibility
    def add_task_from_form_response(self, form_response: Dict[str, Any]) -> Dict[str, Any]:
        """Add task from Google Forms response"""
        return self.add_task_from_api({
            'property_name': form_response.get('Property', ''),
            'task_description': form_response.get('Task Description', form_response.get('TaskDescription', '')),
            'due_date': form_response.get('Due Date', form_response.get('DueDate', '')),
            'priority': form_response.get('Priority', 'Medium'),
            'reporter_email': form_response.get('Reporter Email', form_response.get('ReporterEmail', ''))
        })
    
    def mark_task_complete_by_description(self, task_description: str) -> Optional[int]:
        """Mark task complete by description"""
        all_tasks = self.get_all_tasks()
        for task in all_tasks:
            if task_description.lower() in task.get('task_description', '').lower():
                if task.get('status', '').lower() != 'completed':
                    row_number = task.get('row_number')
                    if row_number:
                        self.mark_task_complete(row_number)
                        return row_number
        return None
    
    def process_sms_command(self, sms_text: str, sender_phone: Optional[str] = None) -> Dict[str, Any]:
        """Process SMS commands"""
        sms_text = sms_text.strip()
        command_parts = sms_text.split(' ', 1)
        
        if len(command_parts) < 2:
            return {"success": False, "message": "Invalid command format"}
        
        command = command_parts[0].upper()
        content = command_parts[1]
        
        if command == "DONE":
            row_completed = self.mark_task_complete_by_description(content)
            if row_completed:
                return {"success": True, "message": f"Task completed: {content}", "row": row_completed}
            return {"success": False, "message": f"Task not found: {content}"}
        
        elif command == "LIST":
            property_tasks = self.get_tasks_by_property(content)
            pending = [t for t in property_tasks if t.get('status', '').lower() == 'pending']
            if pending:
                task_list = "\n".join([f"- {t.get('task_description', '')}" for t in pending])
                return {"success": True, "message": f"Pending tasks for {content}:\n{task_list}"}
            return {"success": True, "message": f"No pending tasks for {content}"}
        
        return {"success": False, "message": "Commands: DONE [task], LIST [property]"}
    
    def send_confirmation_email(
        self, 
        to_email: str, 
        task_description: str, 
        property_name: str, 
        action: str = "added"
    ) -> bool:
        """Send confirmation email (placeholder)"""
        logger.info(f"Email would be sent to {to_email} about {action} task")
        return True
    
    def add_emergency_maintenance_task(
        self,
        property_name: str,
        task_description: str,
        estimated_cost: float,
        actual_cost: Optional[float] = None,
        emergency_type: str = "Urgent"
    ) -> Dict[str, Any]:
        """Add emergency task with cost tracking"""
        result = self.add_task_from_api({
            'property_name': property_name,
            'task_description': f"[EMERGENCY] {task_description}",
            'due_date': datetime.now().strftime('%Y-%m-%d'),
            'priority': emergency_type,
            'category': 'Emergency',
            'estimated_cost': estimated_cost,
            'notes': f"Actual cost: ${actual_cost}" if actual_cost else ""
        })
        
        if result.get('success'):
            return {
                "success": True,
                "message": f"Emergency task logged: {task_description}",
                "estimated_cost": estimated_cost
            }
        return result
    
    def get_emergency_cost_analysis(self) -> Dict[str, Any]:
        """Analyze emergency maintenance costs"""
        all_tasks = self.get_all_tasks()
        emergency_tasks = [t for t in all_tasks if '[EMERGENCY]' in t.get('task_description', '')]
        
        if not emergency_tasks:
            return {"message": "No emergency cost data available yet"}
        
        total_estimated = sum(t.get('estimated_cost', 0) for t in emergency_tasks)
        avg_estimated = total_estimated / len(emergency_tasks) if emergency_tasks else 0
        over_2000 = len([t for t in emergency_tasks if t.get('estimated_cost', 0) >= 2000])
        
        return {
            "total_emergencies": len(emergency_tasks),
            "avg_estimated_cost": round(avg_estimated, 2),
            "over_2000_count": over_2000,
            "validation_message": f"Data shows {over_2000} of {len(emergency_tasks)} emergencies cost $2,000+"
        }

if __name__ == "__main__":
    logger.info("PropertyManagementTracker module loaded successfully")
