{\rtf1\ansi\ansicpg1252\cocoartf2865
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import gspread\
from oauth2client.service_account import ServiceAccountCredentials\
import os\
import smtplib\
from email.mime.text import MIMEText\
from email.mime.multipart import MIMEMultipart\
from datetime import datetime\
\
class PropertyMaintenanceTracker:\
    def __init__(self, credentials_file, spreadsheet_name):\
        # Check if credentials file exists\
        if not os.path.exists(credentials_file):\
            raise FileNotFoundError(\
                f"Credentials file not found: \{credentials_file\}\\n"\
                f"Please ensure you have:\\n"\
                f"1. Created a Google Cloud Service Account\\n"\
                f"2. Downloaded the JSON credentials file\\n"\
                f"3. Placed it at the specified path\\n"\
                f"4. Enabled Google Sheets and Google Drive APIs"\
            )\
        \
        # Set up the credentials\
        scope = ['https://spreadsheets.google.com/feeds',\
                 'https://www.googleapis.com/auth/drive']\
        credentials = ServiceAccountCredentials.from_json_keyfile_name(\
            credentials_file, scope)\
        \
        # Authorize and open the spreadsheet\
        gc = gspread.authorize(credentials)\
        self.spreadsheet = gc.open(spreadsheet_name)\
        \
        # Try to get the worksheet - first try "Maintenance Tasks", then fall back to first sheet\
        try:\
            self.tasks_sheet = self.spreadsheet.worksheet("Maintenance Tasks")\
        except:\
            # Use the first worksheet (usually "Sheet1")\
            self.tasks_sheet = self.spreadsheet.sheet1\
    \
    def add_maintenance_task(self, property_name, task_description, \
                           due_date, priority="Medium", category="General", \
                           estimated_cost=0, notes="", reporter_email=""):\
        """Add a new maintenance task to the tracking sheet with proper column mapping"""\
        from datetime import datetime\
        \
        # Get the next available row\
        tasks = self.tasks_sheet.get_all_values()\
        next_row = len(tasks) + 1\
        \
        # Convert due_date to MM-DD-YYYY format if it's in YYYY-MM-DD format\
        if due_date and len(due_date) == 10 and due_date.count('-') == 2:\
            try:\
                # Parse date and convert to MM-DD-YYYY\
                date_obj = datetime.strptime(due_date, '%Y-%m-%d')\
                due_date = "'" + date_obj.strftime('%m-%d-%Y')  # Prefix with ' to force text format\
            except:\
                pass  # Keep original format if parsing fails\
        \
        # Add the new task with proper column mapping:\
        # Column 1: Property Address\
        # Column 2: Task Description  \
        # Column 3: Category\
        # Column 4: Priority\
        # Column 5: Status\
        # Column 6: Due Date\
        # Column 7: Completed Date (empty for new tasks)\
        # Column 8: Estimated Cost\
        # Column 9: Emergency Cost (empty for now)\
        # Column 10: Notes\
        # Column 11: Reporter Email\
        \
        self.tasks_sheet.update_cell(next_row, 1, property_name)        # Property Address\
        self.tasks_sheet.update_cell(next_row, 2, task_description)     # Task Description\
        self.tasks_sheet.update_cell(next_row, 3, category)             # Category\
        self.tasks_sheet.update_cell(next_row, 4, priority)             # Priority\
        self.tasks_sheet.update_cell(next_row, 5, "Pending")            # Status\
        self.tasks_sheet.update_cell(next_row, 6, due_date)             # Due Date\
        # Column 7 (Completed Date) left empty for new tasks\
        self.tasks_sheet.update_cell(next_row, 8, str(estimated_cost))  # Estimated Cost\
        # Column 9 (Emergency Cost) left empty for now\
        self.tasks_sheet.update_cell(next_row, 10, notes)               # Notes\
        self.tasks_sheet.update_cell(next_row, 11, reporter_email)      # Reporter Email\
        \
        return f"Task added: \{task_description\} for \{property_name\}"\
    \
    def add_task_from_api(self, task_data):\
        """\
        Add task from API request - handles the full task data from React app\
        """\
        try:\
            result = self.add_maintenance_task(\
                property_name=task_data.get('property_name', ''),\
                task_description=task_data.get('task_description', ''),\
                due_date=task_data.get('due_date', ''),\
                priority=task_data.get('priority', 'Medium'),\
                category=task_data.get('category', 'General'),\
                estimated_cost=task_data.get('estimated_cost', 0),\
                notes=task_data.get('notes', ''),\
                reporter_email=task_data.get('reporter_email', '')\
            )\
            return \{"success": True, "message": result\}\
        except Exception as e:\
            return \{"success": False, "message": f"Error adding task: \{str(e)\}"\}\
    \
    def get_all_tasks(self):\
        """Get all tasks in a standardized format compatible with React frontend"""\
        try:\
            all_records = self.tasks_sheet.get_all_records()\
            \
            # Normalize field names for React app compatibility\
            normalized_tasks = []\
            for i, record in enumerate(all_records, start=2):  # Start at 2 because header is row 1\
                normalized_task = \{\
                    # Primary format for React app\
                    "id": f"task_\{i\}",\
                    "row_number": i,\
                    "property_name": record.get('Property Address', ''),\
                    "property_address": record.get('Property Address', ''),\
                    "task_description": record.get('Task Description', ''),\
                    "task_name": record.get('Task Description', ''),\
                    "category": record.get('Category', 'General'),\
                    "priority": record.get('Priority', 'Medium'),\
                    "status": record.get('Status', 'Pending'),\
                    "due_date": self._convert_date_format(record.get('Due Date', '')),\
                    "completed_date": self._convert_date_format(record.get('Completed Date', '')),\
                    "estimated_cost": self._convert_to_float(record.get('Estimated Cost', 0)),\
                    "emergency_cost": self._convert_to_float(record.get('Emergency Cost', 0)),\
                    "emergency_cost_if_delayed": self._convert_to_float(record.get('Emergency Cost', 0)),\
                    "notes": record.get('Notes', ''),\
                    "description": record.get('Notes', ''),\
                    "reporter_email": record.get('Reporter Email', ''),\
                    "created_date": record.get('Date Created', ''),\
                    \
                    # Legacy format for backward compatibility\
                    "Property": record.get('Property Address', ''),\
                    "Property Address": record.get('Property Address', ''),\
                    "Task Description": record.get('Task Description', ''),\
                    "Category": record.get('Category', 'General'),\
                    "Priority": record.get('Priority', 'Medium'),\
                    "Status": record.get('Status', 'Pending'),\
                    "Due Date": record.get('Due Date', ''),\
                    "Completed Date": record.get('Completed Date', ''),\
                    "Estimated Cost": self._convert_to_float(record.get('Estimated Cost', 0)),\
                    "Emergency Cost": self._convert_to_float(record.get('Emergency Cost', 0)),\
                    "Notes": record.get('Notes', ''),\
                    "Reporter Email": record.get('Reporter Email', ''),\
                    "Date Created": record.get('Date Created', ''),\
                \}\
                normalized_tasks.append(normalized_task)\
            \
            return normalized_tasks\
        except Exception as e:\
            print(f"Error getting tasks: \{e\}")\
            return []\
    \
    def _convert_date_format(self, date_str):\
        """Convert MM-DD-YYYY to YYYY-MM-DD for React frontend"""\
        if not date_str:\
            return ''\
        try:\
            from datetime import datetime\
            # Try MM-DD-YYYY format first\
            date_obj = datetime.strptime(date_str, '%m-%d-%Y')\
            return date_obj.strftime('%Y-%m-%d')\
        except ValueError:\
            # If already in YYYY-MM-DD format, return as is\
            try:\
                datetime.strptime(date_str, '%Y-%m-%d')\
                return date_str\
            except ValueError:\
                return date_str  # Return original if can't parse\
    \
    def _convert_to_float(self, value):\
        """Convert string/int to float safely"""\
        if isinstance(value, (int, float)):\
            return float(value)\
        if isinstance(value, str):\
            try:\
                return float(value.replace('$', '').replace(',', ''))\
            except (ValueError, AttributeError):\
                return 0.0\
        return 0.0\
    \
    def mark_task_complete(self, row_number):\
        """Mark a task as complete by row number"""\
        from datetime import datetime\
        \
        self.tasks_sheet.update_cell(row_number, 5, "Completed")  # Status column\
        self.tasks_sheet.update_cell(row_number, 7, "'" + datetime.now().strftime('%m-%d-%Y'))  # Completed Date column (MM-DD-YYYY as text)\
        return f"Task in row \{row_number\} marked as complete"\
    \
    def get_pending_tasks(self):\
        """Get all pending maintenance tasks"""\
        all_tasks = self.tasks_sheet.get_all_records()\
        pending_tasks = [task for task in all_tasks if task.get(\
  'Status', '') == 'Pending']\
        return pending_tasks\
    \
    def get_tasks_by_property(self, property_name):\
        """Get all tasks for a specific property"""\
        all_tasks = self.tasks_sheet.get_all_records()\
        property_tasks = [task for task in all_tasks if task.get(\
            'Property', '') == property_name]\
        return property_tasks\
    \
    def add_task_from_form_response(self, form_response):\
        """\
        Add task from Google Forms response - supports mobile form integration\
        Expected form_response format: \{\
            'Property': str,\
            'Task Description': str,\
            'Due Date': str,\
            'Priority': str,\
            'Reporter Email': str (optional)\
        \}\
        """\
        property_name = form_response.get('Property', '')\
        task_description = form_response.get('Task Description', '')\
        due_date = form_response.get('Due Date', '')\
        priority = form_response.get('Priority', 'Medium')\
        reporter_email = form_response.get('Reporter Email', '')\
        \
        # Get the next available row\
        tasks = self.tasks_sheet.get_all_values()\
        next_row = len(tasks) + 1\
        \
        # Add the new task with form response data\
        self.tasks_sheet.update_cell(next_row, 1, property_name)\
        self.tasks_sheet.update_cell(next_row, 2, task_description)\
        self.tasks_sheet.update_cell(next_row, 3, due_date)\
        self.tasks_sheet.update_cell(next_row, 4, priority)\
        self.tasks_sheet.update_cell(next_row, 5, "Pending")\
        if reporter_email:\
            self.tasks_sheet.update_cell(next_row, 6, reporter_email)\
        \
        return \{\
            'success': True,\
            'message': f"Task added from form: \{task_description\} for \{property_name\}",\
            'row_number': next_row\
        \}\
    \
    def mark_task_complete_by_description(self, task_description):\
        """\
        Mark task complete by description - useful for SMS 'DONE [task]' functionality\
        Returns the row number of completed task or None if not found\
        """\
        from datetime import datetime\
        \
        all_tasks = self.tasks_sheet.get_all_values()\
        for i, row in enumerate(all_tasks[1:], start=2):  # Skip header row\
            if len(row) >= 5 and task_description.lower() in row[1].lower():\
                if row[4] != "Completed":  # Only update if not already completed\
                    self.tasks_sheet.update_cell(i, 5, "Completed")  # Status column\
                    self.tasks_sheet.update_cell(i, 7, "'" + datetime.now().strftime('%m-%d-%Y'))  # Completed Date column (MM-DD-YYYY as text)\
                    return i\
        return None\
    \
    def send_confirmation_email(self, to_email, task_description, property_name, action="added"):\
        """\
        Send confirmation email for task updates\
        Supports your research question about effective reminder psychology\
        """\
        try:\
            # Email configuration (you'll need to set these up)\
            smtp_server = "smtp.gmail.com"  # Change based on your email provider\
            smtp_port = 587\
            sender_email = "your-email@gmail.com"  # Replace with your email\
            sender_password = "your-app-password"  # Use app password for Gmail\
            \
            msg = MIMEMultipart()\
            msg['From'] = sender_email\
            msg['To'] = to_email\
            msg['Subject'] = f"Maintenance Task \{action.title()\}: \{property_name\}"\
            \
            # Positive, action-oriented language to reduce reminder fatigue\
            body = f"""\
            Great news! Your maintenance task has been \{action\}:\
            \
            Property: \{property_name\}\
            Task: \{task_description\}\
            Date: \{datetime.now().strftime('%B %d, %Y at %I:%M %p')\}\
            \
            This proactive maintenance helps protect your property value and prevents costly emergency repairs.\
            \
            Questions? Reply to this email.\
            \
            Best regards,\
            Property Maintenance Tracker\
            """\
            \
            msg.attach(MIMEText(body, 'plain'))\
            \
            server = smtplib.SMTP(smtp_server, smtp_port)\
            server.starttls()\
            server.login(sender_email, sender_password)\
            text = msg.as_string()\
            server.sendmail(sender_email, to_email, text)\
            server.quit()\
            \
            return True\
        except Exception as e:\
            print(f"Email sending failed: \{e\}")\
            return False\
    \
    def get_overdue_tasks(self):\
        """\
        Get overdue tasks for reminder emails\
        Helps address your question about effective reminder timing\
        """\
        all_tasks = self.tasks_sheet.get_all_records()\
        overdue_tasks = []\
        current_date = datetime.now().date()\
        \
        for task in all_tasks:\
            if task.get('Status', '') == 'Pending':\
                try:\
                    due_date = datetime.strptime(task.get('Due Date', ''), '%Y-%m-%d').date()\
                    if due_date < current_date:\
                        overdue_tasks.append(task)\
                except ValueError:\
                    continue  # Skip tasks with invalid date format\
        \
        return overdue_tasks\
    \
    def process_sms_command(self, sms_text, sender_phone=None):\
        """\
        Process SMS commands like 'DONE Fix leaking faucet'\
        Supports your research into simple SMS integration under $20/month\
        \
        Commands:\
        - 'DONE [task description]' - marks task as complete\
        - 'LIST [property]' - shows pending tasks for property\
        - 'ADD [property] [task] [date]' - adds new task\
        """\
        sms_text = sms_text.strip()\
        command_parts = sms_text.split(' ', 1)\
        \
        if len(command_parts) < 2:\
            return \{"success": False, "message": "Invalid command format"\}\
        \
        command = command_parts[0].upper()\
        content = command_parts[1]\
        \
        if command == "DONE":\
            row_completed = self.mark_task_complete_by_description(content)\
            if row_completed:\
                return \{\
                    "success": True, \
                    "message": f"\uc0\u9989  Task completed: \{content\}",\
                    "row": row_completed\
                \}\
            else:\
                return \{\
                    "success": False, \
                    "message": f"\uc0\u10060  Task not found: \{content\}"\
                \}\
        \
        elif command == "LIST":\
            property_tasks = self.get_tasks_by_property(content)\
            pending_tasks = [task for task in property_tasks if task.get('Status') == 'Pending']\
            if pending_tasks:\
                task_list = "\\n".join([f"\'95 \{task.get('Task Description', '')\}" for task in pending_tasks])\
                return \{\
                    "success": True,\
                    "message": f"\uc0\u55357 \u56523  Pending tasks for \{content\}:\\n\{task_list\}"\
                \}\
            else:\
                return \{\
                    "success": True,\
                    "message": f"\uc0\u10024  No pending tasks for \{content\}"\
                \}\
        \
        elif command == "ADD":\
            # Format: ADD [property] [task] [date]\
            parts = content.split(' ', 2)\
            if len(parts) >= 3:\
                property_name, task_desc, due_date = parts\
                result = self.add_maintenance_task(property_name, task_desc, due_date)\
                return \{"success": True, "message": f"\uc0\u9989  \{result\}"\}\
            else:\
                return \{"success": False, "message": "Format: ADD [property] [task] [date]"\}\
        \
        else:\
            return \{\
                "success": False, \
                "message": "Commands: DONE [task], LIST [property], ADD [property] [task] [date]"\
            \}\
    \
    def add_emergency_maintenance_task(self, property_name, task_description, \
                                     estimated_cost, actual_cost=None, emergency_type="Urgent"):\
        """\
        Track emergency maintenance with cost data\
        Helps validate your $2,000+ emergency cost estimates for market research\
        """\
        # Get the next available row\
        tasks = self.tasks_sheet.get_all_values()\
        next_row = len(tasks) + 1\
        \
        # Add emergency task with cost tracking\
        self.tasks_sheet.update_cell(next_row, 1, property_name)\
        self.tasks_sheet.update_cell(next_row, 2, f"[EMERGENCY] \{task_description\}")\
        self.tasks_sheet.update_cell(next_row, 3, datetime.now().strftime('%Y-%m-%d'))\
        self.tasks_sheet.update_cell(next_row, 4, emergency_type)\
        self.tasks_sheet.update_cell(next_row, 5, "Emergency")\
        self.tasks_sheet.update_cell(next_row, 7, f"$\{estimated_cost\}")  # Column G for estimated cost\
        if actual_cost:\
            self.tasks_sheet.update_cell(next_row, 8, f"$\{actual_cost\}")  # Column H for actual cost\
        \
        return \{\
            "success": True,\
            "message": f"Emergency task logged: \{task_description\}",\
            "estimated_cost": estimated_cost,\
            "row": next_row\
        \}\
    \
    def get_emergency_cost_analysis(self):\
        """\
        Analyze emergency maintenance costs to validate your market research\
        Returns data to support your $2,000+ emergency cost claims\
        """\
        all_tasks = self.tasks_sheet.get_all_values()\
        emergency_costs = []\
        \
        for row in all_tasks[1:]:  # Skip header\
            if len(row) >= 8 and "[EMERGENCY]" in row[1]:\
                try:\
                    estimated = float(row[6].replace('$', '').replace(',', '')) if row[6] else 0\
                    actual = float(row[7].replace('$', '').replace(',', '')) if len(row) > 7 and row[7] else None\
                    \
                    emergency_costs.append(\{\
                        'property': row[0],\
                        'task': row[1],\
                        'estimated_cost': estimated,\
                        'actual_cost': actual,\
                        'cost_variance': actual - estimated if actual else None\
                    \})\
                except (ValueError, IndexError):\
                    continue\
        \
        if emergency_costs:\
            total_estimated = sum(task['estimated_cost'] for task in emergency_costs)\
            avg_estimated = total_estimated / len(emergency_costs)\
            \
            completed_costs = [task for task in emergency_costs if task['actual_cost']]\
            if completed_costs:\
                total_actual = sum(task['actual_cost'] for task in completed_costs)\
                avg_actual = total_actual / len(completed_costs)\
                \
                return \{\
                    "total_emergencies": len(emergency_costs),\
                    "avg_estimated_cost": avg_estimated,\
                    "avg_actual_cost": avg_actual,\
                    "cost_overrun_rate": (avg_actual - avg_estimated) / avg_estimated if avg_estimated > 0 else 0,\
                    "over_2000_count": len([task for task in emergency_costs if task['estimated_cost'] >= 2000]),\
                    "validation_message": f"Data shows \{len([task for task in emergency_costs if task['estimated_cost'] >= 2000])\} of \{len(emergency_costs)\} emergencies cost $2,000+"\
                \}\
        \
        return \{"message": "No emergency cost data available yet"\}\
\
    def delete_task(self, row_number):\
        """Delete a task by row number"""\
        try:\
            self.tasks_sheet.delete_rows(row_number)\
            return \{"success": True, "message": f"Task in row \{row_number\} deleted successfully"\}\
        except Exception as e:\
            return \{"success": False, "message": f"Failed to delete task: \{str(e)\}"\}\
\
    def update_task_status(self, row_number, status, completed_date=None):\
        """Update task status and completion date"""\
        try:\
            # Update status column (Column E)\
            self.tasks_sheet.update(f'E\{row_number\}', status)\
            \
            # If marking as completed and no completed_date provided, use today's date\
            if status.lower() == 'completed' and not completed_date:\
                from datetime import datetime\
                completed_date = datetime.now().strftime('%m-%d-%Y')\
            \
            # Update completed date column (Column F) if provided\
            if completed_date:\
                self.tasks_sheet.update(f'F\{row_number\}', completed_date)\
            \
            return \{"success": True, "message": f"Task status updated to \{status\}"\}\
        except Exception as e:\
            return \{"success": False, "message": f"Failed to update task: \{str(e)\}"\}\
\
    def get_dashboard_stats(self):\
        """Get comprehensive dashboard statistics"""\
        try:\
            all_tasks = self.get_all_tasks()\
            \
            total_tasks = len(all_tasks)\
            pending_tasks = len([task for task in all_tasks if task.get('status', '').lower() == 'pending'])\
            completed_tasks = len([task for task in all_tasks if task.get('status', '').lower() == 'completed'])\
            \
            # Calculate overdue tasks\
            from datetime import datetime\
            today = datetime.now()\
            overdue_count = 0\
            \
            for task in all_tasks:\
                if task.get('status', '').lower() != 'completed':\
                    due_date_str = task.get('due_date', '')\
                    if due_date_str:\
                        try:\
                            # Handle MM-DD-YYYY format\
                            due_date = datetime.strptime(due_date_str, '%m-%d-%Y')\
                            if due_date < today:\
                                overdue_count += 1\
                        except ValueError:\
                            # Try other date formats if needed\
                            try:\
                                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')\
                                if due_date < today:\
                                    overdue_count += 1\
                            except ValueError:\
                                pass\
            \
            # Calculate costs\
            preventive_cost = 0\
            emergency_cost_averted = 0\
            \
            for task in all_tasks:\
                estimated_cost = task.get('estimated_cost', 0)\
                if isinstance(estimated_cost, str):\
                    try:\
                        estimated_cost = float(estimated_cost)\
                    except (ValueError, TypeError):\
                        estimated_cost = 0\
                \
                if task.get('status', '').lower() == 'completed':\
                    preventive_cost += estimated_cost\
                    # Assume 6x cost multiplier for emergency repairs\
                    emergency_cost_averted += estimated_cost * 6\
            \
            net_savings = emergency_cost_averted - preventive_cost\
            \
            return \{\
                "total_tasks": total_tasks,\
                "pending": pending_tasks,\
                "overdue": overdue_count,\
                "completed": completed_tasks,\
                "preventive_cost": preventive_cost,\
                "emergency_cost_averted": emergency_cost_averted,\
                "net_savings": net_savings\
            \}\
            \
        except Exception as e:\
            print(f"Error calculating dashboard stats: \{e\}")\
            return \{\
                "total_tasks": 0,\
                "pending": 0,\
                "overdue": 0,\
                "completed": 0,\
                "preventive_cost": 0,\
                "emergency_cost_averted": 0,\
                "net_savings": 0\
            \}\
\
# Example usage\
if __name__ == "__main__":\
    # Replace with your actual file paths and sheet name\
    credentials_path = '/Users/eruzehaji/Desktop/PMT/credentials.json'\
    \
    try:\
        tracker = PropertyMaintenanceTracker(credentials_path, 'PMT-Project')\
        \
        # Add a new task\
        print(tracker.add_maintenance_task("123 Main St", "Fix leaking faucet", "2023-10-30", "High"))\
        \
        # Get pending tasks\
        pending = tracker.get_pending_tasks()\
        print(f"You have \{len(pending)\} pending tasks")\
        \
        # Get tasks for a specific property\
        property_tasks = tracker.get_tasks_by_property("123 Main St")\
        print(f"123 Main St has \{len(property_tasks)\} maintenance tasks")\
        \
    except FileNotFoundError as e:\
        print(f"Setup Error: \{e\}")\
        print("\\nTo set up Google Sheets API credentials:")\
        print("1. Go to Google Cloud Console (console.cloud.google.com)")\
        print("2. Create a new project or select existing one")\
        print("3. Enable Google Sheets API and Google Drive API")\
        print("4. Create a Service Account in IAM & Admin")\
        print("5. Download the JSON key file")\
        print("6. Save it as 'credentials.json' in your project folder")\
        print("7. Share your Google Sheet with the service account email")\
    except Exception as e:\
        print(f"Error: \{e\}")\
}