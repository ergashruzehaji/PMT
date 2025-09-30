import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class PropertyMaintenanceTracker:
    def __init__(self, credentials_file, spreadsheet_name):
        # Check if credentials file exists
        if not os.path.exists(credentials_file):
            raise FileNotFoundError(
                f"Credentials file not found: {credentials_file}\n"
                f"Please ensure you have:\n"
                f"1. Created a Google Cloud Service Account\n"
                f"2. Downloaded the JSON credentials file\n"
                f"3. Placed it at the specified path\n"
                f"4. Enabled Google Sheets and Google Drive APIs"
            )
        
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
    
    def add_maintenance_task(self, property_name, task_description, 
  due_date, priority="Medium"):
        """Add a new maintenance task to the tracking sheet"""
        # Get the next available row
        tasks = self.tasks_sheet.get_all_values()
        next_row = len(tasks) + 1
        
        # Add the new task
        self.tasks_sheet.update_cell(next_row, 1, property_name)
        self.tasks_sheet.update_cell(next_row, 2, task_description)
        self.tasks_sheet.update_cell(next_row, 3, due_date)
        self.tasks_sheet.update_cell(next_row, 4, priority)
        self.tasks_sheet.update_cell(next_row, 5, "Pending")
        
        return f"Task added: {task_description} for {property_name}"
    
    def mark_task_complete(self, row_number):
        """Mark a task as complete by row number"""
        self.tasks_sheet.update_cell(row_number, 5, "Completed")
        return f"Task in row {row_number} marked as complete"
    
    def get_pending_tasks(self):
        """Get all pending maintenance tasks"""
        all_tasks = self.tasks_sheet.get_all_records()
        pending_tasks = [task for task in all_tasks if task.get(
  'Status', '') == 'Pending']
        return pending_tasks
    
    def get_tasks_by_property(self, property_name):
        """Get all tasks for a specific property"""
        all_tasks = self.tasks_sheet.get_all_records()
        property_tasks = [task for task in all_tasks if task.get(
            'Property', '') == property_name]
        return property_tasks
    
    def add_task_from_form_response(self, form_response):
        """
        Add task from Google Forms response - supports mobile form integration
        Expected form_response format: {
            'Property': str,
            'Task Description': str,
            'Due Date': str,
            'Priority': str,
            'Reporter Email': str (optional)
        }
        """
        property_name = form_response.get('Property', '')
        task_description = form_response.get('Task Description', '')
        due_date = form_response.get('Due Date', '')
        priority = form_response.get('Priority', 'Medium')
        reporter_email = form_response.get('Reporter Email', '')
        
        # Get the next available row
        tasks = self.tasks_sheet.get_all_values()
        next_row = len(tasks) + 1
        
        # Add the new task with form response data
        self.tasks_sheet.update_cell(next_row, 1, property_name)
        self.tasks_sheet.update_cell(next_row, 2, task_description)
        self.tasks_sheet.update_cell(next_row, 3, due_date)
        self.tasks_sheet.update_cell(next_row, 4, priority)
        self.tasks_sheet.update_cell(next_row, 5, "Pending")
        if reporter_email:
            self.tasks_sheet.update_cell(next_row, 6, reporter_email)
        
        return {
            'success': True,
            'message': f"Task added from form: {task_description} for {property_name}",
            'row_number': next_row
        }
    
    def mark_task_complete_by_description(self, task_description):
        """
        Mark task complete by description - useful for SMS 'DONE [task]' functionality
        Returns the row number of completed task or None if not found
        """
        all_tasks = self.tasks_sheet.get_all_values()
        for i, row in enumerate(all_tasks[1:], start=2):  # Skip header row
            if len(row) >= 5 and task_description.lower() in row[1].lower():
                if row[4] != "Completed":  # Only update if not already completed
                    self.tasks_sheet.update_cell(i, 5, "Completed")
                    return i
        return None
    
    def send_confirmation_email(self, to_email, task_description, property_name, action="added"):
        """
        Send confirmation email for task updates
        Supports your research question about effective reminder psychology
        """
        try:
            # Email configuration (you'll need to set these up)
            smtp_server = "smtp.gmail.com"  # Change based on your email provider
            smtp_port = 587
            sender_email = "your-email@gmail.com"  # Replace with your email
            sender_password = "your-app-password"  # Use app password for Gmail
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = f"Maintenance Task {action.title()}: {property_name}"
            
            # Positive, action-oriented language to reduce reminder fatigue
            body = f"""
            Great news! Your maintenance task has been {action}:
            
            Property: {property_name}
            Task: {task_description}
            Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            
            This proactive maintenance helps protect your property value and prevents costly emergency repairs.
            
            Questions? Reply to this email.
            
            Best regards,
            Property Maintenance Tracker
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def get_overdue_tasks(self):
        """
        Get overdue tasks for reminder emails
        Helps address your question about effective reminder timing
        """
        all_tasks = self.tasks_sheet.get_all_records()
        overdue_tasks = []
        current_date = datetime.now().date()
        
        for task in all_tasks:
            if task.get('Status', '') == 'Pending':
                try:
                    due_date = datetime.strptime(task.get('Due Date', ''), '%Y-%m-%d').date()
                    if due_date < current_date:
                        overdue_tasks.append(task)
                except ValueError:
                    continue  # Skip tasks with invalid date format
        
        return overdue_tasks
    
    def process_sms_command(self, sms_text, sender_phone=None):
        """
        Process SMS commands like 'DONE Fix leaking faucet'
        Supports your research into simple SMS integration under $20/month
        
        Commands:
        - 'DONE [task description]' - marks task as complete
        - 'LIST [property]' - shows pending tasks for property
        - 'ADD [property] [task] [date]' - adds new task
        """
        sms_text = sms_text.strip()
        command_parts = sms_text.split(' ', 1)
        
        if len(command_parts) < 2:
            return {"success": False, "message": "Invalid command format"}
        
        command = command_parts[0].upper()
        content = command_parts[1]
        
        if command == "DONE":
            row_completed = self.mark_task_complete_by_description(content)
            if row_completed:
                return {
                    "success": True, 
                    "message": f"✅ Task completed: {content}",
                    "row": row_completed
                }
            else:
                return {
                    "success": False, 
                    "message": f"❌ Task not found: {content}"
                }
        
        elif command == "LIST":
            property_tasks = self.get_tasks_by_property(content)
            pending_tasks = [task for task in property_tasks if task.get('Status') == 'Pending']
            if pending_tasks:
                task_list = "\n".join([f"• {task.get('Task Description', '')}" for task in pending_tasks])
                return {
                    "success": True,
                    "message": f"📋 Pending tasks for {content}:\n{task_list}"
                }
            else:
                return {
                    "success": True,
                    "message": f"✨ No pending tasks for {content}"
                }
        
        elif command == "ADD":
            # Format: ADD [property] [task] [date]
            parts = content.split(' ', 2)
            if len(parts) >= 3:
                property_name, task_desc, due_date = parts
                result = self.add_maintenance_task(property_name, task_desc, due_date)
                return {"success": True, "message": f"✅ {result}"}
            else:
                return {"success": False, "message": "Format: ADD [property] [task] [date]"}
        
        else:
            return {
                "success": False, 
                "message": "Commands: DONE [task], LIST [property], ADD [property] [task] [date]"
            }
    
    def add_emergency_maintenance_task(self, property_name, task_description, 
                                     estimated_cost, actual_cost=None, emergency_type="Urgent"):
        """
        Track emergency maintenance with cost data
        Helps validate your $2,000+ emergency cost estimates for market research
        """
        # Get the next available row
        tasks = self.tasks_sheet.get_all_values()
        next_row = len(tasks) + 1
        
        # Add emergency task with cost tracking
        self.tasks_sheet.update_cell(next_row, 1, property_name)
        self.tasks_sheet.update_cell(next_row, 2, f"[EMERGENCY] {task_description}")
        self.tasks_sheet.update_cell(next_row, 3, datetime.now().strftime('%Y-%m-%d'))
        self.tasks_sheet.update_cell(next_row, 4, emergency_type)
        self.tasks_sheet.update_cell(next_row, 5, "Emergency")
        self.tasks_sheet.update_cell(next_row, 7, f"${estimated_cost}")  # Column G for estimated cost
        if actual_cost:
            self.tasks_sheet.update_cell(next_row, 8, f"${actual_cost}")  # Column H for actual cost
        
        return {
            "success": True,
            "message": f"Emergency task logged: {task_description}",
            "estimated_cost": estimated_cost,
            "row": next_row
        }
    
    def get_emergency_cost_analysis(self):
        """
        Analyze emergency maintenance costs to validate your market research
        Returns data to support your $2,000+ emergency cost claims
        """
        all_tasks = self.tasks_sheet.get_all_values()
        emergency_costs = []
        
        for row in all_tasks[1:]:  # Skip header
            if len(row) >= 8 and "[EMERGENCY]" in row[1]:
                try:
                    estimated = float(row[6].replace('$', '').replace(',', '')) if row[6] else 0
                    actual = float(row[7].replace('$', '').replace(',', '')) if len(row) > 7 and row[7] else None
                    
                    emergency_costs.append({
                        'property': row[0],
                        'task': row[1],
                        'estimated_cost': estimated,
                        'actual_cost': actual,
                        'cost_variance': actual - estimated if actual else None
                    })
                except (ValueError, IndexError):
                    continue
        
        if emergency_costs:
            total_estimated = sum(task['estimated_cost'] for task in emergency_costs)
            avg_estimated = total_estimated / len(emergency_costs)
            
            completed_costs = [task for task in emergency_costs if task['actual_cost']]
            if completed_costs:
                total_actual = sum(task['actual_cost'] for task in completed_costs)
                avg_actual = total_actual / len(completed_costs)
                
                return {
                    "total_emergencies": len(emergency_costs),
                    "avg_estimated_cost": avg_estimated,
                    "avg_actual_cost": avg_actual,
                    "cost_overrun_rate": (avg_actual - avg_estimated) / avg_estimated if avg_estimated > 0 else 0,
                    "over_2000_count": len([task for task in emergency_costs if task['estimated_cost'] >= 2000]),
                    "validation_message": f"Data shows {len([task for task in emergency_costs if task['estimated_cost'] >= 2000])} of {len(emergency_costs)} emergencies cost $2,000+"
                }
        
        return {"message": "No emergency cost data available yet"}

# Example usage
if __name__ == "__main__":
    # Replace with your actual file paths and sheet name
    credentials_path = '/Users/eruzehaji/Desktop/PMT/credentials.json'
    
    try:
        tracker = PropertyMaintenanceTracker(credentials_path, 'Property Management Tracker')
        
        # Add a new task
        print(tracker.add_maintenance_task("123 Main St", "Fix leaking faucet", "2023-10-30", "High"))
        
        # Get pending tasks
        pending = tracker.get_pending_tasks()
        print(f"You have {len(pending)} pending tasks")
        
        # Get tasks for a specific property
        property_tasks = tracker.get_tasks_by_property("123 Main St")
        print(f"123 Main St has {len(property_tasks)} maintenance tasks")
        
    except FileNotFoundError as e:
        print(f"Setup Error: {e}")
        print("\nTo set up Google Sheets API credentials:")
        print("1. Go to Google Cloud Console (console.cloud.google.com)")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Sheets API and Google Drive API")
        print("4. Create a Service Account in IAM & Admin")
        print("5. Download the JSON key file")
        print("6. Save it as 'credentials.json' in your project folder")
        print("7. Share your Google Sheet with the service account email")
    except Exception as e:
        print(f"Error: {e}")