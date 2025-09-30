"""
Enhanced Property Maintenance Tracker with both PostgreSQL and Google Sheets support
Fallback system: PostgreSQL primary, Google Sheets backup
"""
import os
import json
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

# Import database models
try:
    from database import (
        get_db, create_tables, get_task_stats, add_days_until_due,
        MaintenanceTask, Property, MaintenanceHistory,
        TaskCreate, TaskUpdate, TaskResponse, PropertyCreate, PropertyResponse
    )
    DATABASE_AVAILABLE = True
except Exception as e:
    print(f"Database not available: {e}")
    DATABASE_AVAILABLE = False

# Import Google Sheets (with fallback)
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    SHEETS_AVAILABLE = True
except ImportError as e:
    print(f"Google Sheets libraries not available: {e}")
    SHEETS_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(
    title="Property Maintenance Tracker API - Enhanced",
    description="Professional property maintenance with PostgreSQL and Google Sheets integration",
    version="2.5.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for data sources
db_available = False
sheets_available = False
sheets_client = None
worksheet = None

class GoogleSheetsManager:
    def __init__(self):
        self.client = None
        self.worksheet = None
        self.setup_sheets()
    
    def setup_sheets(self):
        """Set up Google Sheets connection"""
        try:
            if not SHEETS_AVAILABLE:
                return False
                
            # Get credentials from environment
            creds_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
            sheet_url = os.getenv('GOOGLE_SHEETS_URL')
            
            if not creds_json or not sheet_url:
                print("Google Sheets credentials or URL not found in environment")
                return False
            
            # Parse credentials
            creds_dict = json.loads(creds_json)
            
            # Set up credentials
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            self.client = gspread.authorize(credentials)
            
            # Open the spreadsheet
            self.worksheet = self.client.open_by_url(sheet_url).sheet1
            
            # Initialize headers if sheet is empty
            if not self.worksheet.get_all_values():
                headers = [
                    'ID', 'Property Address', 'Task Name', 'Description', 'Category',
                    'Priority', 'Status', 'Due Date', 'Completed Date', 'Estimated Cost',
                    'Actual Cost', 'Emergency Cost If Delayed', 'Notes', 'Created At'
                ]
                self.worksheet.append_row(headers)
            
            print("Google Sheets connection established successfully")
            return True
            
        except Exception as e:
            print(f"Failed to setup Google Sheets: {e}")
            return False
    
    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks from Google Sheets"""
        try:
            if not self.worksheet:
                return []
            
            records = self.worksheet.get_all_records()
            tasks = []
            
            for record in records:
                if record.get('Task Name'):  # Only process non-empty rows
                    task = {
                        'id': record.get('ID', ''),
                        'property_address': record.get('Property Address', ''),
                        'task_name': record.get('Task Name', ''),
                        'description': record.get('Description', ''),
                        'category': record.get('Category', 'Other'),
                        'priority': record.get('Priority', 'Medium'),
                        'status': record.get('Status', 'Pending'),
                        'due_date': record.get('Due Date', ''),
                        'completed_date': record.get('Completed Date', ''),
                        'estimated_cost': float(record.get('Estimated Cost', 0) or 0),
                        'actual_cost': float(record.get('Actual Cost', 0) or 0) if record.get('Actual Cost') else None,
                        'emergency_cost_if_delayed': float(record.get('Emergency Cost If Delayed', 0) or 0),
                        'notes': record.get('Notes', ''),
                        'created_at': record.get('Created At', '')
                    }
                    tasks.append(task)
            
            return tasks
        except Exception as e:
            print(f"Error getting tasks from Google Sheets: {e}")
            return []
    
    def add_task(self, task_data: Dict) -> bool:
        """Add task to Google Sheets"""
        try:
            if not self.worksheet:
                return False
            
            # Generate ID
            existing_tasks = self.get_all_tasks()
            next_id = max([int(t.get('id', 0) or 0) for t in existing_tasks], default=0) + 1
            
            row = [
                next_id,
                task_data.get('property_address', ''),
                task_data.get('task_name', ''),
                task_data.get('description', ''),
                task_data.get('category', 'Other'),
                task_data.get('priority', 'Medium'),
                task_data.get('status', 'Pending'),
                task_data.get('due_date', ''),
                task_data.get('completed_date', ''),
                task_data.get('estimated_cost', 0),
                task_data.get('actual_cost', ''),
                task_data.get('emergency_cost_if_delayed', 0),
                task_data.get('notes', ''),
                datetime.now().isoformat()
            ]
            
            self.worksheet.append_row(row)
            return True
            
        except Exception as e:
            print(f"Error adding task to Google Sheets: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Calculate stats from Google Sheets data"""
        try:
            tasks = self.get_all_tasks()
            
            total_tasks = len(tasks)
            pending = len([t for t in tasks if t['status'] == 'Pending'])
            completed = len([t for t in tasks if t['status'] == 'Completed'])
            
            # Calculate overdue
            today = date.today()
            overdue = 0
            for task in tasks:
                if task['status'] != 'Completed' and task['due_date']:
                    try:
                        due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                        if due_date < today:
                            overdue += 1
                    except:
                        pass
            
            # Calculate costs
            preventive_cost = sum([t.get('actual_cost', 0) or 0 for t in tasks if t['status'] == 'Completed'])
            emergency_cost_averted = sum([t.get('emergency_cost_if_delayed', 0) or 0 for t in tasks if t['status'] == 'Completed'])
            net_savings = emergency_cost_averted - preventive_cost
            
            return {
                'total_tasks': total_tasks,
                'pending': pending,
                'overdue': overdue,
                'completed': completed,
                'preventive_cost': preventive_cost,
                'emergency_cost_averted': emergency_cost_averted,
                'net_savings': net_savings
            }
        except Exception as e:
            print(f"Error calculating stats from Google Sheets: {e}")
            return {
                'total_tasks': 0, 'pending': 0, 'overdue': 0, 'completed': 0,
                'preventive_cost': 0, 'emergency_cost_averted': 0, 'net_savings': 0
            }

# Initialize data sources
sheets_manager = GoogleSheetsManager()

@app.on_event("startup")
async def startup_event():
    global db_available, sheets_available
    
    # Try to initialize database
    if DATABASE_AVAILABLE:
        try:
            create_tables()
            db_available = True
            print("✅ PostgreSQL database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            db_available = False
    
    # Check Google Sheets
    sheets_available = sheets_manager.client is not None
    if sheets_available:
        print("✅ Google Sheets connection established")
    else:
        print("❌ Google Sheets not available")
    
    print(f"Data sources available: PostgreSQL={db_available}, Google Sheets={sheets_available}")

# Mock data fallback
mock_tasks = [
    {
        "id": 1,
        "property_address": "123 Demo Street, Demo City, DC 12345",
        "task_name": "HVAC Filter Replacement",
        "description": "Replace air filters in main HVAC system",
        "category": "HVAC",
        "priority": "Medium",
        "status": "Pending",
        "due_date": "2024-11-15",
        "completed_date": None,
        "estimated_cost": 75.00,
        "actual_cost": None,
        "emergency_cost_if_delayed": 1500.00,
        "notes": "Use MERV 13 filters",
        "created_at": "2024-10-01T10:00:00"
    },
    {
        "id": 2,
        "property_address": "456 Sample Ave, Example Town, ET 67890",
        "task_name": "Gutter Cleaning",
        "description": "Clean and inspect all gutters",
        "category": "Exterior",
        "priority": "High",
        "status": "Overdue",
        "due_date": "2024-10-15",
        "completed_date": None,
        "estimated_cost": 200.00,
        "actual_cost": None,
        "emergency_cost_if_delayed": 3000.00,
        "notes": "Check for loose fasteners",
        "created_at": "2024-09-15T14:30:00"
    }
]

def get_data_source():
    """Determine which data source to use"""
    if db_available:
        return "postgresql"
    elif sheets_available:
        return "sheets"
    else:
        return "mock"

# Health check endpoint
@app.get("/health")
async def health_check():
    data_source = get_data_source()
    return {
        "status": "healthy",
        "service": "Property Maintenance Tracker API Enhanced",
        "version": "2.5.0",
        "timestamp": datetime.now().isoformat(),
        "data_sources": {
            "postgresql": db_available,
            "google_sheets": sheets_available,
            "active": data_source
        }
    }

# Tasks endpoints
@app.get("/api/tasks")
async def get_tasks(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db) if DATABASE_AVAILABLE else None
):
    """Get all tasks from available data source"""
    data_source = get_data_source()
    
    try:
        if data_source == "postgresql" and db:
            # Use PostgreSQL
            query = db.query(MaintenanceTask)
            if status:
                query = query.filter(MaintenanceTask.status == status)
            if category:
                query = query.filter(MaintenanceTask.category == category)
            if priority:
                query = query.filter(MaintenanceTask.priority == priority)
            
            tasks = query.order_by(MaintenanceTask.due_date).all()
            return [add_days_until_due(task) for task in tasks]
            
        elif data_source == "sheets":
            # Use Google Sheets
            tasks = sheets_manager.get_all_tasks()
            
            # Apply filters
            if status:
                tasks = [t for t in tasks if t.get('status') == status]
            if category:
                tasks = [t for t in tasks if t.get('category') == category]
            if priority:
                tasks = [t for t in tasks if t.get('priority') == priority]
            
            return tasks
            
        else:
            # Use mock data
            tasks = mock_tasks.copy()
            
            # Apply filters
            if status:
                tasks = [t for t in tasks if t.get('status') == status]
            if category:
                tasks = [t for t in tasks if t.get('category') == category]
            if priority:
                tasks = [t for t in tasks if t.get('priority') == priority]
            
            return tasks
            
    except Exception as e:
        print(f"Error in get_tasks: {e}")
        return mock_tasks

@app.post("/api/tasks")
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db) if DATABASE_AVAILABLE else None
):
    """Create a new task"""
    data_source = get_data_source()
    
    try:
        if data_source == "postgresql" and db:
            # Use PostgreSQL
            db_task = MaintenanceTask(**task_data.dict())
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            return add_days_until_due(db_task)
            
        elif data_source == "sheets":
            # Use Google Sheets
            success = sheets_manager.add_task(task_data.dict())
            if success:
                return {"message": "Task created successfully in Google Sheets"}
            else:
                raise HTTPException(status_code=500, detail="Failed to create task in Google Sheets")
                
        else:
            # Mock response
            new_task = task_data.dict()
            new_task["id"] = max([t["id"] for t in mock_tasks], default=0) + 1
            new_task["created_at"] = datetime.now().isoformat()
            mock_tasks.append(new_task)
            return new_task
            
    except Exception as e:
        print(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_dashboard_stats(db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    """Get dashboard statistics"""
    data_source = get_data_source()
    
    try:
        if data_source == "postgresql" and db:
            # Use PostgreSQL
            stats = get_task_stats(db)
            
        elif data_source == "sheets":
            # Use Google Sheets
            stats = sheets_manager.get_stats()
            
        else:
            # Use mock data
            stats = {
                "total_tasks": len(mock_tasks),
                "pending": len([t for t in mock_tasks if t["status"] == "Pending"]),
                "overdue": len([t for t in mock_tasks if t["status"] == "Overdue"]),
                "completed": len([t for t in mock_tasks if t["status"] == "Completed"]),
                "preventive_cost": sum([t.get("actual_cost", 0) or 0 for t in mock_tasks if t["status"] == "Completed"]),
                "emergency_cost_averted": sum([t.get("emergency_cost_if_delayed", 0) or 0 for t in mock_tasks if t["status"] == "Completed"]),
                "net_savings": 0  # Will be calculated properly
            }
            stats["net_savings"] = stats["emergency_cost_averted"] - stats["preventive_cost"]
        
        return {
            "success": True,
            "stats": stats,
            "data_source": data_source
        }
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {
            "success": False,
            "error": str(e),
            "stats": {
                "total_tasks": 0, "pending": 0, "overdue": 0, "completed": 0,
                "preventive_cost": 0, "emergency_cost_averted": 0, "net_savings": 0
            },
            "data_source": "error"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))