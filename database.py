"""
Database configuration and models for Property Maintenance Tracker
"""
import os
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# Database URL from Railway environment
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./maintenance.db')

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True)
    property_type = Column(String)  # Single Family, Apartment, etc.
    square_footage = Column(Integer)
    year_built = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, index=True)
    property_address = Column(String, index=True)
    task_name = Column(String)
    description = Column(Text)
    category = Column(String)  # HVAC, Plumbing, Electrical, etc.
    priority = Column(String)  # High, Medium, Low
    status = Column(String, default="Pending")  # Pending, In Progress, Completed, Overdue
    due_date = Column(Date)
    completed_date = Column(Date, nullable=True)
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, nullable=True)
    emergency_cost_if_delayed = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MaintenanceHistory(Base):
    __tablename__ = "maintenance_history"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer)
    property_id = Column(Integer)
    action = Column(String)  # Created, Updated, Completed
    description = Column(Text)
    cost = Column(Float, nullable=True)
    performed_by = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Pydantic Models for API
class PropertyCreate(BaseModel):
    address: str
    property_type: str
    square_footage: Optional[int] = None
    year_built: Optional[int] = None

class PropertyResponse(BaseModel):
    id: int
    address: str
    property_type: str
    square_footage: Optional[int]
    year_built: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    property_address: str
    task_name: str
    description: str
    category: str
    priority: str = "Medium"
    due_date: date
    estimated_cost: float = 0.0
    emergency_cost_if_delayed: float = 0.0
    notes: Optional[str] = None

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    actual_cost: Optional[float] = None
    notes: Optional[str] = None
    completed_date: Optional[date] = None

class TaskResponse(BaseModel):
    id: int
    property_address: str
    task_name: str
    description: str
    category: str
    priority: str
    status: str
    due_date: date
    completed_date: Optional[date]
    estimated_cost: float
    actual_cost: Optional[float]
    emergency_cost_if_delayed: float
    notes: Optional[str]
    created_at: datetime
    days_until_due: Optional[int] = None

    class Config:
        from_attributes = True

# Database functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_task_stats(db: Session):
    """Get dashboard statistics"""
    from sqlalchemy import func
    
    total_tasks = db.query(MaintenanceTask).count()
    pending = db.query(MaintenanceTask).filter(MaintenanceTask.status == "Pending").count()
    completed = db.query(MaintenanceTask).filter(MaintenanceTask.status == "Completed").count()
    
    # Calculate overdue tasks (due date passed and not completed)
    today = date.today()
    overdue = db.query(MaintenanceTask).filter(
        MaintenanceTask.due_date < today,
        MaintenanceTask.status != "Completed"
    ).count()
    
    # Calculate costs
    preventive_cost = db.query(func.sum(MaintenanceTask.actual_cost)).filter(
        MaintenanceTask.status == "Completed"
    ).scalar() or 0
    
    # Emergency cost averted (estimated emergency costs for completed preventive tasks)
    emergency_cost_averted = db.query(func.sum(MaintenanceTask.emergency_cost_if_delayed)).filter(
        MaintenanceTask.status == "Completed"
    ).scalar() or 0
    
    net_savings = emergency_cost_averted - preventive_cost
    
    return {
        "total_tasks": total_tasks,
        "pending": pending,
        "overdue": overdue,
        "completed": completed,
        "preventive_cost": float(preventive_cost),
        "emergency_cost_averted": float(emergency_cost_averted),
        "net_savings": float(net_savings)
    }

def add_days_until_due(task: MaintenanceTask) -> TaskResponse:
    """Add calculated days_until_due field to task"""
    task_dict = {
        "id": task.id,
        "property_address": task.property_address,
        "task_name": task.task_name,
        "description": task.description,
        "category": task.category,
        "priority": task.priority,
        "status": task.status,
        "due_date": task.due_date,
        "completed_date": task.completed_date,
        "estimated_cost": task.estimated_cost,
        "actual_cost": task.actual_cost,
        "emergency_cost_if_delayed": task.emergency_cost_if_delayed,
        "notes": task.notes,
        "created_at": task.created_at,
        "days_until_due": (task.due_date - date.today()).days if task.status != "Completed" else None
    }
    return TaskResponse(**task_dict)