from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import json
import tempfile
from maintenance_tracker import PropertyMaintenanceTracker

# Initialize FastAPI app
app = FastAPI(title="Property Maintenance Tracker API", version="2.0.0")

# Add CORS middleware to allow React frontend and Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",  # React dev servers
        "https://pmt-production-8f79794d.up.railway.app",
        "https://web-production-8f79794d.up.railway.app", 
        "https://lavish-presence-production.up.railway.app",
        "https://pmt-production.up.railway.app",
        "https://*.up.railway.app"  # Allow any Railway subdomain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
# Pydantic models for API requests/responses
class TaskCreate(BaseModel):
    property_name: str
    task_description: str
    due_date: str
    priority: str = "Medium"
    category: str = "General"
    estimated_cost: float = 0.0
    emergency_cost: float = 0.0
    notes: str = ""
    reporter_email: str = ""

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    completed_date: Optional[str] = None
    notes: Optional[str] = None

class FormResponse(BaseModel):
    Property: str
    TaskDescription: str = None
    DueDate: str
    Priority: str = "Medium"
    ReporterEmail: Optional[str] = None

class SMSCommand(BaseModel):
    sms_text: str
    sender_phone: Optional[str] = None

class EmergencyTask(BaseModel):
    property_name: str
    task_description: str
    estimated_cost: float
    actual_cost: Optional[float] = None
    emergency_type: str = "Urgent"

class EmailNotification(BaseModel):
    to_email: str
    task_description: str
    property_name: str
    action: str = "added"

# Mock data for when Google Sheets is not available
mock_tasks = [
    {
        "property_name": "Demo Property", 
        "task_description": "Check HVAC system", 
        "due_date": "2025-10-15", 
        "priority": "High",
        "status": "Pending",
        "estimated_cost": 150.0,
        "created_date": "2025-09-30"
    },
    {
        "property_name": "Demo Property", 
        "task_description": "Inspect plumbing", 
        "due_date": "2025-10-20", 
        "priority": "Medium",
        "status": "Pending", 
        "estimated_cost": 200.0,
        "created_date": "2025-09-30"
    }
]

# Initialize the tracker (you'll need to handle this per user in production)
def initialize_tracker():
    """Initialize tracker with environment variables or local credentials"""
    try:
        # Try to get credentials from environment variable (for Railway/Heroku)
        google_creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        spreadsheet_name = os.getenv('SPREADSHEET_NAME', 'Property Management Tracker')
        
        print(f"🔍 Initializing tracker...")
        print(f"📊 Spreadsheet name: {spreadsheet_name}")
        print(f"🔑 Google credentials available: {bool(google_creds_json)}")
        
        if google_creds_json:
            print(f"📋 Credentials length: {len(google_creds_json)} characters")
            
            try:
                # Parse JSON from environment variable
                import tempfile
                creds_dict = json.loads(google_creds_json)
                print(f"✅ JSON parsed successfully, type: {creds_dict.get('type', 'unknown')}")
                
                # Create temporary credentials file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                    json.dump(creds_dict, temp_file)
                    temp_creds_path = temp_file.name
                
                print(f"📁 Temp credentials file created: {temp_creds_path}")
                
                tracker = PropertyMaintenanceTracker(temp_creds_path, spreadsheet_name)
                print("✅ Tracker initialized successfully with environment credentials")
                
                # Clean up temporary file
                os.unlink(temp_creds_path)
                
                return tracker
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                return None
            except Exception as e:
                print(f"❌ Error initializing with environment credentials: {e}")
                return None
        else:
            print("🔄 No environment credentials, trying local file...")
            # Fall back to local credentials file
            local_creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
            print(f"📁 Checking local credentials at: {local_creds_path}")
            if os.path.exists(local_creds_path):
                print("📄 Local credentials file found, initializing tracker...")
                try:
                    tracker = PropertyMaintenanceTracker(local_creds_path, spreadsheet_name)
                    print("✅ Tracker initialized successfully with local credentials!")
                    return tracker
                except Exception as e:
                    print(f"❌ Error initializing with local credentials: {e}")
                    return None
            else:
                print("❌ Local credentials file not found")
                return None
                
    except Exception as e:
        print(f"Warning: Could not initialize tracker: {e}")
        return None

tracker = initialize_tracker()

@app.get("/")
async def root():
    return {"message": "Property Maintenance Tracker API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "tracker_available": tracker is not None}

# Task management endpoints
@app.post("/api/tasks")
async def create_task(task: TaskCreate):
    """Create a new maintenance task"""
    if not tracker:
        # Use mock data when tracker is not available
        new_task = {
            "id": f"task_mock_{len(mock_tasks) + 1}",
            "property_address": task.property_name,
            "property_name": task.property_name,
            "task_description": task.task_description,
            "task_name": task.task_description,
            "category": task.category,
            "priority": task.priority,
            "status": "Pending",
            "due_date": task.due_date,
            "created_date": "2025-09-30",
            "completed_date": "",
            "estimated_cost": task.estimated_cost,
            "emergency_cost": task.emergency_cost,
            "emergency_cost_if_delayed": task.emergency_cost,
            "notes": task.notes,
            "description": task.notes,
            "reporter_email": task.reporter_email,
            # Legacy format for compatibility
            "Property": task.property_name,
            "Task Description": task.task_description,
            "Category": task.category,
            "Priority": task.priority,
            "Status": "Pending",
            "Due Date": task.due_date,
            "Estimated Cost": task.estimated_cost,
            "Emergency Cost": task.emergency_cost
        }
        mock_tasks.append(new_task)
        return {"success": True, "message": "Task added successfully (demo mode)"}
    
    try:
        result = tracker.add_task_from_api(task.dict())
        return {"success": result["success"], "message": result["message"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def get_all_tasks():
    """Get all tasks with their status"""
    if not tracker:
        # Return mock data when tracker is not available
        return {"success": True, "tasks": mock_tasks}
    
    try:
        # Get all tasks from the sheet using new standardized format
        all_tasks = tracker.get_all_tasks()
        return {"success": True, "tasks": all_tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: str, update_data: TaskUpdate):
    """Update a task status or other fields"""
    if not tracker:
        # Update mock data
        for task in mock_tasks:
            if str(task.get("id", "")) == str(task_id):
                if update_data.status:
                    task["status"] = update_data.status
                    task["Status"] = update_data.status  # Legacy compatibility
                if update_data.completed_date:
                    task["completed_date"] = update_data.completed_date
                elif update_data.status and update_data.status.lower() == "completed":
                    from datetime import datetime
                    task["completed_date"] = datetime.now().strftime('%Y-%m-%d')
                if update_data.notes:
                    task["notes"] = update_data.notes
                    task["description"] = update_data.notes
                return {"success": True, "message": f"Task {task_id} updated successfully (demo mode)"}
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        # Extract row number from task_id
        if str(task_id).startswith('task_'):
            row_number = int(task_id.split('_')[1])
        else:
            row_number = int(task_id) + 1  # Add 1 for header row
        
        if update_data.status:
            result = tracker.update_task_status(
                row_number, 
                update_data.status, 
                update_data.completed_date
            )
            return {"success": result["success"], "message": result["message"]}
        else:
            return {"success": False, "message": "No update data provided"}
            
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid task ID format: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/pending")
async def get_pending_tasks():
    """Get all pending maintenance tasks"""
    if not tracker:
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        pending_tasks = tracker.get_pending_tasks()
        return {"success": True, "tasks": pending_tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/overdue")
async def get_overdue_tasks():
    """Get all overdue tasks"""
    if not tracker:
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        overdue_tasks = tracker.get_overdue_tasks()
        return {"success": True, "tasks": overdue_tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/property/{property_name}")
async def get_tasks_by_property(property_name: str):
    """Get all tasks for a specific property"""
    if not tracker:
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        property_tasks = tracker.get_tasks_by_property(property_name)
        return {"success": True, "tasks": property_tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/tasks/{row_number}/complete")
async def mark_task_complete(row_number: int):
    """Mark a task as complete by row number"""
    if not tracker:
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        result = tracker.mark_task_complete(row_number)
        return {"success": True, "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/tasks/complete")
async def mark_task_complete_by_description(task_description: str):
    """Mark task complete by description - useful for SMS integration"""
    if not tracker:
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        row_number = tracker.mark_task_complete_by_description(task_description)
        if row_number:
            return {"success": True, "message": f"Task completed", "row": row_number}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Google Forms integration
@app.post("/api/forms/response")
async def handle_form_response(form_response: FormResponse):
    """Handle Google Forms response"""
    if not tracker:
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        # Convert Pydantic model to dict for the tracker
        response_dict = {
            'Property': form_response.Property,
            'Task Description': form_response.TaskDescription,
            'Due Date': form_response.DueDate,
            'Priority': form_response.Priority,
            'Reporter Email': form_response.ReporterEmail
        }
        result = tracker.add_task_from_form_response(response_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SMS integration
@app.post("/api/sms/command")
async def process_sms_command(sms_command: SMSCommand):
    """Process SMS commands like 'DONE Fix leaking faucet'"""
    if not tracker:
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        result = tracker.process_sms_command(
            sms_command.sms_text, 
            sms_command.sender_phone
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Emergency maintenance
@app.post("/api/emergency")
async def create_emergency_task(emergency: EmergencyTask):
    """Create emergency maintenance task with cost tracking"""
    if not tracker:
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        result = tracker.add_emergency_maintenance_task(
            emergency.property_name,
            emergency.task_description,
            emergency.estimated_cost,
            emergency.actual_cost,
            emergency.emergency_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/emergency/analysis")
async def get_emergency_cost_analysis():
    """Get emergency cost analysis for market research"""
    if not tracker:
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        analysis = tracker.get_emergency_cost_analysis()
        return {"success": True, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Email notifications
@app.post("/api/notifications/email")
async def send_email_notification(notification: EmailNotification):
    """Send confirmation email for task updates"""
    if not tracker:
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        success = tracker.send_confirmation_email(
            notification.to_email,
            notification.task_description,
            notification.property_name,
            notification.action
        )
        return {"success": success, "message": "Email sent" if success else "Email failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Statistics endpoint for React dashboard
@app.get("/api/stats")
async def get_dashboard_stats():
    """Get dashboard statistics for React frontend"""
    if not tracker:
        # Return mock stats when tracker is not available
        completed_tasks = [task for task in mock_tasks if task.get('status') == 'Completed']
        pending_tasks = [task for task in mock_tasks if task.get('status') == 'Pending']
        
        preventive_cost = sum(float(task.get('estimated_cost', 0)) for task in completed_tasks)
        emergency_cost_averted = preventive_cost * 6  # 6x multiplier
        
        stats = {
            "total_tasks": len(mock_tasks),
            "pending": len(pending_tasks),
            "overdue": 0,  # No overdue logic in mock data
            "completed": len(completed_tasks),
            "preventive_cost": preventive_cost,
            "emergency_cost_averted": emergency_cost_averted,
            "net_savings": emergency_cost_averted - preventive_cost
        }
        
        return {"success": True, "stats": stats}
    
    try:
        stats = tracker.get_dashboard_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        print(f"Error getting stats: {e}")
        # Return basic stats as fallback
        try:
            all_tasks = tracker.get_all_tasks()
            total_tasks = len(all_tasks)
            pending_tasks = len([task for task in all_tasks if task.get('status', '').lower() == 'pending'])
            
            stats = {
                "total_tasks": total_tasks,
                "pending": pending_tasks,
                "overdue": 0,
                "completed": total_tasks - pending_tasks,
                "preventive_cost": 0,
                "emergency_cost_averted": 0,
                "net_savings": 0
            }
            
            return {"success": True, "stats": stats}
        except Exception as e2:
            raise HTTPException(status_code=500, detail=str(e2))

if __name__ == "__main__":
    print("🚀 Starting Property Maintenance Tracker API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("⚠️  Note: Some features require Google Sheets credentials")
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)