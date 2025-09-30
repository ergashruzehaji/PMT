from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import json
from maintenance_tracker import PropertyMaintenanceTracker

# Initialize FastAPI app
app = FastAPI(title="Property Maintenance Tracker API", version="1.0.0")

# Add CORS middleware to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class TaskCreate(BaseModel):
    property_name: str
    task_description: str
    due_date: str
    priority: str = "Medium"

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

# Initialize the tracker (you'll need to handle this per user in production)
def initialize_tracker():
    """Initialize tracker with environment variables or local credentials"""
    try:
        # Try to get credentials from environment variable (for Railway/Heroku)
        google_creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        spreadsheet_name = os.getenv('SPREADSHEET_NAME', 'Property Management Tracker')
        
        if google_creds_json:
            # Parse JSON from environment variable
            import tempfile
            creds_dict = json.loads(google_creds_json)
            
            # Create temporary credentials file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(creds_dict, temp_file)
                temp_creds_path = temp_file.name
            
            tracker = PropertyMaintenanceTracker(temp_creds_path, spreadsheet_name)
            
            # Clean up temporary file
            os.unlink(temp_creds_path)
            
            return tracker
        else:
            # Fall back to local credentials file
            local_creds_path = '/Users/eruzehaji/Desktop/PMT/credentials.json'
            if os.path.exists(local_creds_path):
                return PropertyMaintenanceTracker(local_creds_path, spreadsheet_name)
            else:
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
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        result = tracker.add_maintenance_task(
            task.property_name, 
            task.task_description, 
            task.due_date, 
            task.priority
        )
        return {"success": True, "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def get_all_tasks():
    """Get all tasks with their status"""
    if not tracker:
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        # Get all tasks from the sheet
        all_tasks = tracker.tasks_sheet.get_all_records()
        return {"success": True, "tasks": all_tasks}
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
        raise HTTPException(status_code=500, detail="Tracker not initialized")
    
    try:
        all_tasks = tracker.tasks_sheet.get_all_records()
        pending_tasks = tracker.get_pending_tasks()
        overdue_tasks = tracker.get_overdue_tasks()
        
        # Calculate cost savings (similar to React logic)
        completed_tasks = [task for task in all_tasks if task.get('Status') == 'Completed']
        preventive_cost = sum(float(task.get('Cost', 0)) for task in completed_tasks if task.get('Cost'))
        emergency_cost_averted = preventive_cost * 6  # 6x multiplier
        
        stats = {
            "total_tasks": len(all_tasks),
            "pending": len(pending_tasks),
            "overdue": len(overdue_tasks),
            "completed": len(completed_tasks),
            "preventive_cost": preventive_cost,
            "emergency_cost_averted": emergency_cost_averted,
            "net_savings": emergency_cost_averted - preventive_cost
        }
        
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Property Maintenance Tracker API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("⚠️  Note: Some features require Google Sheets credentials")
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)