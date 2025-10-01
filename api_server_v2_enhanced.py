from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import json
from maintenance_tracker_v2 import PropertyMaintenanceTracker

# Initialize FastAPI app
app = FastAPI(title="Property Maintenance Tracker API", version="2.0.0")

# Add CORS middleware to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
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
    category: str = "General"
    estimated_cost: float = 0.0
    emergency_cost: float = 0.0
    notes: str = ""
    reporter_email: str = ""

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    completed_date: Optional[str] = None
    notes: Optional[str] = None

class TaskResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None

# Initialize tracker
def initialize_tracker():
    """Initialize the maintenance tracker with proper error handling"""
    try:
        # Check for Railway environment variables first
        google_credentials = os.getenv('GOOGLE_CREDENTIALS_JSON')
        spreadsheet_name = os.getenv('GOOGLE_SHEET_NAME', 'Property Management Tracker')
        
        if google_credentials:
            print("Using Google Sheets credentials from environment variable")
            tracker = PropertyMaintenanceTracker(google_credentials, spreadsheet_name)
            print("✅ Google Sheets tracker initialized successfully")
            return tracker
        else:
            print("⚠️ No Google credentials found in environment")
            return None
            
    except Exception as e:
        print(f"❌ Failed to initialize tracker: {e}")
        return None

tracker = initialize_tracker()

# Mock data for when Google Sheets is not available
mock_tasks = [
    {
        "id": "task_demo_1",
        "property_address": "Demo Property 123",
        "property_name": "Demo Property 123",
        "task_description": "Fix leaking faucet in kitchen",
        "task_name": "Fix leaking faucet in kitchen",
        "category": "Plumbing",
        "priority": "High",
        "status": "Pending",
        "due_date": "2025-10-15",
        "created_date": "2025-09-30",
        "completed_date": "",
        "estimated_cost": 150.0,
        "emergency_cost": 900.0,
        "emergency_cost_if_delayed": 900.0,
        "notes": "Kitchen sink faucet dripping constantly",
        "description": "Kitchen sink faucet dripping constantly",
        "reporter_email": "demo@example.com"
    },
    {
        "id": "task_demo_2", 
        "property_address": "Demo Property 456",
        "property_name": "Demo Property 456",
        "task_description": "HVAC filter replacement",
        "task_name": "HVAC filter replacement",
        "category": "HVAC",
        "priority": "Medium",
        "status": "Completed",
        "due_date": "2025-09-25",
        "created_date": "2025-09-15",
        "completed_date": "2025-09-24",
        "estimated_cost": 75.0,
        "emergency_cost": 450.0,
        "emergency_cost_if_delayed": 450.0,
        "notes": "Quarterly HVAC maintenance",
        "description": "Quarterly HVAC maintenance",
        "reporter_email": "demo@example.com"
    }
]

@app.get("/")
async def root():
    return {"message": "Property Maintenance Tracker API v2.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "tracker_available": tracker is not None,
        "google_sheets_connected": tracker is not None,
        "version": "2.0.0"
    }

# Task management endpoints
@app.post("/api/tasks", response_model=TaskResponse)
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
            "reporter_email": task.reporter_email
        }
        mock_tasks.append(new_task)
        return TaskResponse(
            success=True, 
            message="Task added successfully (demo mode)", 
            task_id=new_task["id"]
        )
    
    try:
        result = tracker.add_task_from_api(task.dict())
        return TaskResponse(
            success=result["success"],
            message=result["message"],
            task_id=result.get("task_id")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def get_all_tasks():
    """Get all tasks with their status"""
    if not tracker:
        # Return mock data when tracker is not available
        return {"success": True, "tasks": mock_tasks}
    
    try:
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
            if task["id"] == task_id:
                if update_data.status:
                    task["status"] = update_data.status
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
        if task_id.startswith('task_'):
            row_number = int(task_id.split('_')[1])
        else:
            row_number = int(task_id)
        
        if update_data.status:
            result = tracker.update_task_status(
                row_number, 
                update_data.status, 
                update_data.completed_date
            )
            return {"success": result["success"], "message": result["message"]}
        else:
            return {"success": False, "message": "No update data provided"}
            
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task (for demo purposes, we'll mark as cancelled)"""
    if not tracker:
        # Remove from mock data
        global mock_tasks
        original_length = len(mock_tasks)
        mock_tasks = [task for task in mock_tasks if task["id"] != task_id]
        if len(mock_tasks) < original_length:
            return {"success": True, "message": f"Task {task_id} deleted successfully (demo mode)"}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        # Extract row number from task_id
        if task_id.startswith('task_'):
            row_number = int(task_id.split('_')[1])
        else:
            row_number = int(task_id)
        
        # Mark as cancelled instead of actually deleting
        result = tracker.update_task_status(row_number, "Cancelled")
        return {"success": result["success"], "message": f"Task {task_id} cancelled successfully"}
        
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/pending")
async def get_pending_tasks():
    """Get all pending maintenance tasks"""
    if not tracker:
        pending_mock = [task for task in mock_tasks if task["status"] == "Pending"]
        return {"success": True, "tasks": pending_mock}
    
    try:
        pending_tasks = tracker.get_pending_tasks()
        return {"success": True, "tasks": pending_tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/overdue")
async def get_overdue_tasks():
    """Get all overdue tasks"""
    if not tracker:
        # Mock overdue logic
        from datetime import datetime
        current_date = datetime.now().date()
        overdue_mock = []
        for task in mock_tasks:
            if task["status"] == "Pending":
                try:
                    due_date = datetime.strptime(task["due_date"], '%Y-%m-%d').date()
                    if due_date < current_date:
                        overdue_mock.append(task)
                except ValueError:
                    continue
        return {"success": True, "tasks": overdue_mock}
    
    try:
        overdue_tasks = tracker.get_overdue_tasks()
        return {"success": True, "tasks": overdue_tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_dashboard_stats():
    """Get dashboard statistics for React frontend"""
    if not tracker:
        # Calculate mock stats
        total_tasks = len(mock_tasks)
        pending_tasks = len([t for t in mock_tasks if t["status"] == "Pending"])
        completed_tasks = len([t for t in mock_tasks if t["status"] == "Completed"])
        
        # Calculate overdue
        from datetime import datetime
        current_date = datetime.now().date()
        overdue_count = 0
        for task in mock_tasks:
            if task["status"] == "Pending":
                try:
                    due_date = datetime.strptime(task["due_date"], '%Y-%m-%d').date()
                    if due_date < current_date:
                        overdue_count += 1
                except ValueError:
                    continue
        
        completed = [t for t in mock_tasks if t["status"] == "Completed"]
        preventive_cost = sum(t.get("estimated_cost", 0) for t in completed)
        emergency_cost_averted = sum(t.get("emergency_cost", 0) for t in completed)
        
        stats = {
            "total_tasks": total_tasks,
            "pending": pending_tasks,
            "overdue": overdue_count,
            "completed": completed_tasks,
            "preventive_cost": preventive_cost,
            "emergency_cost_averted": emergency_cost_averted,
            "net_savings": emergency_cost_averted - preventive_cost
        }
        
        return {"success": True, "stats": stats}
    
    try:
        stats = tracker.get_dashboard_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/property/{property_name}")
async def get_tasks_by_property(property_name: str):
    """Get all tasks for a specific property"""
    if not tracker:
        property_tasks = [task for task in mock_tasks if property_name.lower() in task["property_name"].lower()]
        return {"success": True, "tasks": property_tasks}
    
    try:
        property_tasks = tracker.get_tasks_by_property(property_name)
        return {"success": True, "tasks": property_tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint to verify Google Sheets connection
@app.get("/api/health/sheets")
async def check_sheets_connection():
    """Check if Google Sheets connection is working"""
    if not tracker:
        return {
            "connected": False,
            "message": "Google Sheets tracker not initialized",
            "mode": "demo"
        }
    
    try:
        # Try to get a simple count
        tasks = tracker.get_all_tasks()
        return {
            "connected": True,
            "message": f"Google Sheets connected successfully - {len(tasks)} tasks found",
            "task_count": len(tasks),
            "mode": "live"
        }
    except Exception as e:
        return {
            "connected": False,
            "message": f"Google Sheets connection error: {str(e)}",
            "mode": "error"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)