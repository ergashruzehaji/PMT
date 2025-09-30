"""
Enhanced Property Maintenance Tracker API with PostgreSQL
Professional-grade REST API for property maintenance management
"""
import os
from datetime import date, datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from database import (
    get_db, create_tables, get_task_stats, add_days_until_due,
    MaintenanceTask, Property, MaintenanceHistory,
    TaskCreate, TaskUpdate, TaskResponse, PropertyCreate, PropertyResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="Property Maintenance Tracker API",
    description="Professional property maintenance management system",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Property Maintenance Tracker API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Properties endpoints
@app.post("/api/properties", response_model=PropertyResponse)
async def create_property(property_data: PropertyCreate, db: Session = Depends(get_db)):
    """Create a new property"""
    # Check if property already exists
    existing = db.query(Property).filter(Property.address == property_data.address).first()
    if existing:
        raise HTTPException(status_code=400, detail="Property already exists")
    
    db_property = Property(**property_data.dict())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

@app.get("/api/properties", response_model=List[PropertyResponse])
async def get_properties(db: Session = Depends(get_db)):
    """Get all properties"""
    properties = db.query(Property).order_by(Property.address).all()
    return properties

@app.get("/api/properties/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: int, db: Session = Depends(get_db)):
    """Get a specific property"""
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

# Task endpoints
@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """Create a new maintenance task"""
    # Verify property exists or create it
    property = db.query(Property).filter(Property.address == task_data.property_address).first()
    property_id = property.id if property else None
    
    db_task = MaintenanceTask(
        property_id=property_id,
        **task_data.dict()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Add to history
    history = MaintenanceHistory(
        task_id=db_task.id,
        property_id=property_id,
        action="Created",
        description=f"Task '{task_data.task_name}' created for {task_data.property_address}"
    )
    db.add(history)
    db.commit()
    
    return add_days_until_due(db_task)

@app.get("/api/tasks", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    property_address: Optional[str] = Query(None, description="Filter by property"),
    sort_by: str = Query("due_date", description="Sort by field"),
    sort_order: str = Query("asc", description="Sort order (asc/desc)"),
    limit: int = Query(100, description="Maximum number of tasks"),
    db: Session = Depends(get_db)
):
    """Get all maintenance tasks with filtering and sorting"""
    query = db.query(MaintenanceTask)
    
    # Apply filters
    if status:
        query = query.filter(MaintenanceTask.status == status)
    if category:
        query = query.filter(MaintenanceTask.category == category)
    if priority:
        query = query.filter(MaintenanceTask.priority == priority)
    if property_address:
        query = query.filter(MaintenanceTask.property_address.ilike(f"%{property_address}%"))
    
    # Apply sorting
    sort_column = getattr(MaintenanceTask, sort_by, MaintenanceTask.due_date)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    tasks = query.limit(limit).all()
    return [add_days_until_due(task) for task in tasks]

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task"""
    task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return add_days_until_due(task)

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update a maintenance task"""
    task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    # Add to history
    history = MaintenanceHistory(
        task_id=task.id,
        property_id=task.property_id,
        action="Updated",
        description=f"Task '{task.task_name}' updated",
        cost=task_update.actual_cost
    )
    db.add(history)
    db.commit()
    
    return add_days_until_due(task)

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a maintenance task"""
    task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}

# Dashboard and analytics endpoints
@app.get("/api/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        stats = get_task_stats(db)
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stats": {
                "total_tasks": 0,
                "pending": 0,
                "overdue": 0,
                "completed": 0,
                "preventive_cost": 0,
                "emergency_cost_averted": 0,
                "net_savings": 0
            }
        }

@app.get("/api/analytics/categories")
async def get_task_categories(db: Session = Depends(get_db)):
    """Get task distribution by category"""
    from sqlalchemy import func
    
    result = db.query(
        MaintenanceTask.category,
        func.count(MaintenanceTask.id).label('count'),
        func.sum(MaintenanceTask.estimated_cost).label('total_cost')
    ).group_by(MaintenanceTask.category).all()
    
    return [
        {
            "category": row.category,
            "count": row.count,
            "total_cost": float(row.total_cost or 0)
        }
        for row in result
    ]

@app.get("/api/analytics/priorities")
async def get_task_priorities(db: Session = Depends(get_db)):
    """Get task distribution by priority"""
    from sqlalchemy import func
    
    result = db.query(
        MaintenanceTask.priority,
        func.count(MaintenanceTask.id).label('count')
    ).group_by(MaintenanceTask.priority).all()
    
    return [
        {
            "priority": row.priority,
            "count": row.count
        }
        for row in result
    ]

@app.get("/api/analytics/monthly")
async def get_monthly_stats(year: int = Query(2024), db: Session = Depends(get_db)):
    """Get monthly completion statistics"""
    from sqlalchemy import func, extract
    
    result = db.query(
        extract('month', MaintenanceTask.completed_date).label('month'),
        func.count(MaintenanceTask.id).label('completed_tasks'),
        func.sum(MaintenanceTask.actual_cost).label('total_cost')
    ).filter(
        extract('year', MaintenanceTask.completed_date) == year,
        MaintenanceTask.status == 'Completed'
    ).group_by(extract('month', MaintenanceTask.completed_date)).all()
    
    return [
        {
            "month": int(row.month),
            "completed_tasks": row.completed_tasks,
            "total_cost": float(row.total_cost or 0)
        }
        for row in result
    ]

# Utility endpoints
@app.get("/api/categories")
async def get_categories():
    """Get available maintenance categories"""
    return [
        "HVAC",
        "Plumbing", 
        "Electrical",
        "Roofing",
        "Flooring",
        "Windows",
        "Appliances",
        "Exterior",
        "Landscaping",
        "Safety",
        "Other"
    ]

@app.get("/api/priorities")
async def get_priorities():
    """Get available priority levels"""
    return ["High", "Medium", "Low"]

@app.get("/api/statuses")
async def get_statuses():
    """Get available task statuses"""
    return ["Pending", "In Progress", "Completed", "Overdue"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))