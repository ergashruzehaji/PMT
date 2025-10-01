import React, { useState, useEffect } from 'react';
import './App.css';
import { API_BASE_URL } from './config';

// Construction-themed Icons
const Icons = {
  Home: () => <span className="text-2xl">🏗️</span>,
  Tools: () => <span className="text-2xl">🔧</span>,
  Calendar: () => <span className="text-2xl">📅</span>,
  DollarSign: () => <span className="text-2xl">💰</span>,
  TrendingUp: () => <span className="text-2xl">📈</span>,
  AlertTriangle: () => <span className="text-2xl">⚠️</span>,
  CheckCircle: () => <span className="text-2xl">✅</span>,
  Clock: () => <span className="text-2xl">⏰</span>,
  Plus: () => <span className="text-2xl">➕</span>,
  Filter: () => <span className="text-2xl">🔍</span>,
  Edit: () => <span className="text-2xl">✏️</span>,
  Trash: () => <span className="text-2xl">🗑️</span>,
  Bell: () => <span className="text-2xl">🔔</span>,
  Hammer: () => <span className="text-2xl">🔨</span>,
  Wrench: () => <span className="text-2xl">🔧</span>,
  HardHat: () => <span className="text-2xl">⛑️</span>,
  Blueprint: () => <span className="text-2xl">📋</span>
};

// Sound Manager
class SoundManager {
  constructor() {
    this.sounds = {};
    this.createSounds();
  }

  createSounds() {
    // Create bell sound using Web Audio API
    this.createBellSound();
    this.createSuccessSound();
    this.createErrorSound();
  }

  createBellSound() {
    this.sounds.bell = () => {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      // Bell-like frequencies
      oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(400, audioContext.currentTime + 0.1);
      oscillator.frequency.exponentialRampToValueAtTime(300, audioContext.currentTime + 0.3);
      
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
      
      oscillator.type = 'sine';
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.5);
    };
  }

  createSuccessSound() {
    this.sounds.success = () => {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.setValueAtTime(523, audioContext.currentTime); // C5
      oscillator.frequency.setValueAtTime(659, audioContext.currentTime + 0.1); // E5
      oscillator.frequency.setValueAtTime(784, audioContext.currentTime + 0.2); // G5
      
      gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
      
      oscillator.type = 'triangle';
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.3);
    };
  }

  createErrorSound() {
    this.sounds.error = () => {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.setValueAtTime(200, audioContext.currentTime);
      oscillator.frequency.setValueAtTime(150, audioContext.currentTime + 0.1);
      
      gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
      
      oscillator.type = 'square';
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.2);
    };
  }

  play(soundName) {
    if (this.sounds[soundName]) {
      try {
        this.sounds[soundName]();
      } catch (error) {
        console.log('Audio playback not supported or blocked');
      }
    }
  }
}

const soundManager = new SoundManager();

// Professional UI Components
const StatCard = ({ title, value, icon: Icon, type = 'default', trend, trendValue }) => (
  <div className={`stat-card ${type} fadeIn`}>
    <div className="stat-icon">
      <Icon />
    </div>
    <div className="stat-number">{value}</div>
    <div className="stat-label">{title}</div>
    {trend && (
      <div className={`stat-change ${trend}`}>
        {trend === 'positive' ? '↗️' : '↘️'} {trendValue}
      </div>
    )}
  </div>
);

const Badge = ({ children, type = 'default' }) => (
  <span className={`badge badge-${type}`}>
    {children}
  </span>
);

const Button = ({ children, onClick, variant = 'primary', size = 'default', icon: Icon, disabled = false, ...props }) => (
  <button 
    className={`btn btn-${variant} ${size === 'sm' ? 'btn-sm' : ''}`}
    onClick={onClick}
    disabled={disabled}
    {...props}
  >
    {Icon && <Icon />}
    {children}
  </button>
);

const NotificationBell = ({ onClick, hasNotifications = false }) => (
  <button 
    className="notification-bell"
    onClick={() => {
      soundManager.play('bell');
      if (onClick) onClick();
    }}
    title="Notifications"
  >
    <Icons.Bell />
    {hasNotifications && (
      <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
        !
      </span>
    )}
  </button>
);

const TaskItem = ({ task, onUpdate, onDelete }) => {
  const getPriorityType = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return 'priority-medium';
    }
  };

  const getStatusType = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'status-completed';
      case 'pending': return 'status-pending';
      case 'overdue': return 'status-overdue';
      default: return 'status-pending';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const getDaysUntilDue = (dueDate, status) => {
    if (status === 'Completed') return null;
    const today = new Date();
    const due = new Date(dueDate);
    const diffTime = due - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return `${Math.abs(diffDays)} days overdue`;
    if (diffDays === 0) return 'Due today';
    return `${diffDays} days left`;
  };

  const handleComplete = () => {
    soundManager.play('success');
    onUpdate(task.id, { 
      status: 'Completed', 
      completed_date: new Date().toISOString().split('T')[0] 
    });
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      soundManager.play('error');
      onDelete(task.id);
    }
  };

  // Use different property name formats for backward compatibility
  const property = task.property_address || task['Property'] || '';
  const taskName = task.task_name || task['Task Description'] || '';
  const description = task.description || task['Task Description'] || '';
  const category = task.category || task['Category'] || '';
  const priority = task.priority || task['Priority'] || 'Medium';
  const status = task.status || task['Status'] || 'Pending';
  const dueDate = task.due_date || task['Due Date'] || '';
  const estimatedCost = task.estimated_cost || task['Estimated Cost'] || 0;
  const emergencyCost = task.emergency_cost_if_delayed || task['Emergency Cost'] || 0;

  return (
    <div className="task-item slideIn">
      <div className="task-meta">
        <div>
          <div className="task-title">{taskName}</div>
          <div className="task-property">🏠 {property}</div>
        </div>
        <div className="task-badges">
          <Badge type={getPriorityType(priority)}>{priority}</Badge>
          <Badge type={getStatusType(status)}>{status}</Badge>
        </div>
      </div>
      
      {description && <div className="task-description">{description}</div>}
      
      <div className="task-details">
        <div className="task-detail">
          <div className="task-detail-label">🔧 Category</div>
          <div className="task-detail-value">{category}</div>
        </div>
        <div className="task-detail">
          <div className="task-detail-label">📅 Due Date</div>
          <div className="task-detail-value">{formatDate(dueDate)}</div>
        </div>
        <div className="task-detail">
          <div className="task-detail-label">💰 Est. Cost</div>
          <div className="task-detail-value">{formatCurrency(estimatedCost)}</div>
        </div>
        {emergencyCost > 0 && (
          <div className="task-detail">
            <div className="task-detail-label">⚠️ Emergency Cost</div>
            <div className="task-detail-value">{formatCurrency(emergencyCost)}</div>
          </div>
        )}
        {status !== 'Completed' && dueDate && (
          <div className="task-detail">
            <div className="task-detail-label">⏰ Time Left</div>
            <div className="task-detail-value">{getDaysUntilDue(dueDate, status)}</div>
          </div>
        )}
      </div>
      
      <div className="task-actions">
        {status !== 'Completed' && (
          <Button 
            variant="success" 
            size="sm" 
            onClick={handleComplete}
            icon={Icons.CheckCircle}
          >
            Complete
          </Button>
        )}
        <Button 
          variant="secondary" 
          size="sm" 
          onClick={() => console.log('Edit task:', task)}
          icon={Icons.Edit}
        >
          Edit
        </Button>
        <Button 
          variant="danger" 
          size="sm" 
          onClick={handleDelete}
          icon={Icons.Trash}
        >
          Delete
        </Button>
      </div>
    </div>
  );
};

const TaskForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    property_address: '',
    task_name: '',
    description: '',
    category: 'HVAC',
    priority: 'Medium',
    due_date: '',
    estimated_cost: 0,
    emergency_cost_if_delayed: 0,
    notes: ''
  });

  const categories = ['HVAC', 'Plumbing', 'Electrical', 'Roofing', 'Flooring', 'Windows', 'Appliances', 'Exterior', 'Landscaping', 'Safety', 'Other'];
  const priorities = ['High', 'Medium', 'Low'];

  const handleSubmit = (e) => {
    e.preventDefault();
    soundManager.play('success');
    onSubmit(formData);
    setFormData({
      property_address: '',
      task_name: '',
      description: '',
      category: 'HVAC',
      priority: 'Medium',
      due_date: '',
      estimated_cost: 0,
      emergency_cost_if_delayed: 0,
      notes: ''
    });
  };

  return (
    <div className="card fadeIn">
      <div className="card-header">
        <h3 className="card-title">
          <Icons.Tools /> Add New Maintenance Task
        </h3>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">🏠 Property Address</label>
            <input
              type="text"
              className="form-input"
              value={formData.property_address}
              onChange={(e) => setFormData({ ...formData, property_address: e.target.value })}
              required
              placeholder="Enter property address"
            />
          </div>
          <div className="form-group">
            <label className="form-label">🔧 Task Name</label>
            <input
              type="text"
              className="form-input"
              value={formData.task_name}
              onChange={(e) => setFormData({ ...formData, task_name: e.target.value })}
              required
              placeholder="Enter task name"
            />
          </div>
          <div className="form-group">
            <label className="form-label">📂 Category</label>
            <select
              className="form-select"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">⚡ Priority</label>
            <select
              className="form-select"
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
            >
              {priorities.map(pri => (
                <option key={pri} value={pri}>{pri}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">📅 Due Date</label>
            <input
              type="date"
              className="form-input"
              value={formData.due_date}
              onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">💰 Estimated Cost</label>
            <input
              type="number"
              className="form-input"
              value={formData.estimated_cost}
              onChange={(e) => setFormData({ ...formData, estimated_cost: parseFloat(e.target.value) || 0 })}
              min="0"
              step="0.01"
              placeholder="0.00"
            />
          </div>
        </div>
        <div className="form-group">
          <label className="form-label">📝 Description</label>
          <textarea
            className="form-input"
            rows="3"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            required
            placeholder="Describe the maintenance task"
          />
        </div>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '2rem' }}>
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" icon={Icons.Plus}>
            Create Task
          </Button>
        </div>
      </form>
    </div>
  );
};

function App() {
  const [stats, setStats] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    category: '',
    priority: ''
  });

  // API Functions
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      } else {
        throw new Error(data.error || 'Failed to fetch stats');
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError('Failed to load dashboard statistics');
      soundManager.play('error');
    }
  };

  const fetchTasks = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.category) params.append('category', filters.category);
      if (filters.priority) params.append('priority', filters.priority);
      
      const response = await fetch(`${API_BASE_URL}/tasks?${params}`);
      if (!response.ok) throw new Error('Failed to fetch tasks');
      
      const data = await response.json();
      setTasks(data.success ? data.tasks : data);
    } catch (err) {
      console.error('Error fetching tasks:', err);
      setError('Failed to load tasks');
      soundManager.play('error');
    }
  };

  const createTask = async (taskData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData)
      });
      
      if (!response.ok) throw new Error('Failed to create task');
      
      setShowForm(false);
      setSuccess('Task created successfully!');
      soundManager.play('success');
      setTimeout(() => setSuccess(null), 3000);
      fetchTasks();
      fetchStats();
    } catch (err) {
      console.error('Error creating task:', err);
      setError('Failed to create task');
      soundManager.play('error');
    }
  };

  const updateTask = async (taskId, updateData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });
      
      if (!response.ok) throw new Error('Failed to update task');
      
      setSuccess('Task updated successfully!');
      setTimeout(() => setSuccess(null), 3000);
      fetchTasks();
      fetchStats();
    } catch (err) {
      console.error('Error updating task:', err);
      setError('Failed to update task');
      soundManager.play('error');
    }
  };

  const deleteTask = async (taskId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Failed to delete task');
      
      setSuccess('Task deleted successfully!');
      setTimeout(() => setSuccess(null), 3000);
      fetchTasks();
      fetchStats();
    } catch (err) {
      console.error('Error deleting task:', err);
      setError('Failed to delete task');
      soundManager.play('error');
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchTasks()]);
      setLoading(false);
    };
    
    loadData();
  }, [filters]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const hasOverdueTasks = stats && stats.overdue > 0;

  if (loading) {
    return (
      <div className="app-container">
        <div className="loading">
          <div className="spinner"></div>
          <div>Loading Property Maintenance Tracker...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <div className="header-icon">
              <Icons.HardHat />
            </div>
            <div>
              <h1>Property Maintenance Tracker</h1>
              <div className="header-subtitle">Professional Construction Management System</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <NotificationBell 
              hasNotifications={hasOverdueTasks}
              onClick={() => console.log('Notifications clicked')}
            />
            <Button 
              variant="primary" 
              onClick={() => setShowForm(!showForm)}
              icon={Icons.Plus}
            >
              {showForm ? 'Cancel' : 'Add Task'}
            </Button>
          </div>
        </div>
      </header>

      <main className="main-content">
        {error && (
          <div className="error fadeIn">
            <strong>⚠️ Error:</strong> {error}
            <button 
              style={{ float: 'right', background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer', color: 'inherit' }}
              onClick={() => setError(null)}
            >
              ×
            </button>
          </div>
        )}

        {success && (
          <div className="success fadeIn">
            <strong>✅ Success:</strong> {success}
            <button 
              style={{ float: 'right', background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer', color: 'inherit' }}
              onClick={() => setSuccess(null)}
            >
              ×
            </button>
          </div>
        )}

        {/* Dashboard Statistics */}
        {stats && (
          <div className="stats-grid">
            <StatCard
              title="Total Tasks"
              value={stats.total_tasks}
              icon={Icons.Blueprint}
              type="info"
            />
            <StatCard
              title="Pending Tasks"
              value={stats.pending}
              icon={Icons.Clock}
              type="warning"
            />
            <StatCard
              title="Overdue Tasks"
              value={stats.overdue}
              icon={Icons.AlertTriangle}
              type="danger"
            />
            <StatCard
              title="Completed Tasks"
              value={stats.completed}
              icon={Icons.CheckCircle}
              type="success"
            />
            <StatCard
              title="Preventive Cost"
              value={formatCurrency(stats.preventive_cost)}
              icon={Icons.DollarSign}
              type="info"
            />
            <StatCard
              title="Emergency Cost Averted"
              value={formatCurrency(stats.emergency_cost_averted)}
              icon={Icons.TrendingUp}
              type="success"
            />
            <StatCard
              title="Net Savings"
              value={formatCurrency(stats.net_savings)}
              icon={Icons.TrendingUp}
              type={stats.net_savings >= 0 ? "success" : "danger"}
            />
          </div>
        )}

        {/* Add Task Form */}
        {showForm && (
          <div style={{ marginBottom: '2rem' }}>
            <TaskForm 
              onSubmit={createTask}
              onCancel={() => setShowForm(false)}
            />
          </div>
        )}

        {/* Task List */}
        <div className="task-list">
          <div className="task-header">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 className="card-title" style={{ color: 'white', margin: 0 }}>
                <Icons.Hammer /> Maintenance Tasks
              </h2>
              <Icons.Filter />
            </div>
            <div className="task-filters">
              <div className="form-group">
                <select
                  className="form-select"
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                >
                  <option value="">All Statuses</option>
                  <option value="Pending">Pending</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Completed">Completed</option>
                  <option value="Overdue">Overdue</option>
                </select>
              </div>
              <div className="form-group">
                <select
                  className="form-select"
                  value={filters.category}
                  onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                >
                  <option value="">All Categories</option>
                  <option value="HVAC">HVAC</option>
                  <option value="Plumbing">Plumbing</option>
                  <option value="Electrical">Electrical</option>
                  <option value="Roofing">Roofing</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="form-group">
                <select
                  className="form-select"
                  value={filters.priority}
                  onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                >
                  <option value="">All Priorities</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>
            </div>
          </div>
          
          {tasks.length === 0 ? (
            <div style={{ padding: '4rem', textAlign: 'center', color: '#64748b' }}>
              <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🏗️</div>
              <div style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                No maintenance tasks found
              </div>
              <div style={{ fontSize: '0.875rem' }}>
                {showForm ? 'Fill out the form above to create your first task' : 'Click "Add Task" to get started with property maintenance'}
              </div>
            </div>
          ) : (
            tasks.map((task, index) => (
              <TaskItem
                key={task.id || index}
                task={task}
                onUpdate={updateTask}
                onDelete={deleteTask}
              />
            ))
          )}
        </div>
      </main>
    </div>
  );
}

export default App;

// Professional UI Components
const StatCard = ({ title, value, icon: Icon, trend, trendValue, type = 'default' }) => (
  <div className={`stat-card ${type}`}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div>
        <div className="stat-number">{value}</div>
        <div className="stat-label">{title}</div>
        {trend && (
          <div className={`stat-change ${trend}`}>
            {trend === 'positive' ? '↗️' : '↘️'} {trendValue}
          </div>
        )}
      </div>
      <Icon />
    </div>
  </div>
);

const Badge = ({ children, type = 'default' }) => (
  <span className={`badge badge-${type}`}>
    {children}
  </span>
);

const Button = ({ children, onClick, variant = 'primary', size = 'default', icon: Icon, ...props }) => (
  <button 
    className={`btn btn-${variant} ${size === 'sm' ? 'btn-sm' : ''}`}
    onClick={onClick}
    {...props}
  >
    {Icon && <Icon />}
    {children}
  </button>
);

const TaskItem = ({ task, onUpdate, onDelete }) => {
  const getPriorityType = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return 'priority-medium';
    }
  };

  const getStatusType = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'status-completed';
      case 'pending': return 'status-pending';
      case 'overdue': return 'status-overdue';
      default: return 'status-pending';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const getDaysUntilDue = (dueDate, status) => {
    if (status === 'Completed') return null;
    const today = new Date();
    const due = new Date(dueDate);
    const diffTime = due - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return `${Math.abs(diffDays)} days overdue`;
    if (diffDays === 0) return 'Due today';
    return `${diffDays} days left`;
  };

  return (
    <div className="task-item fadeIn">
      <div className="task-meta">
        <div>
          <div className="task-title">{task.task_name}</div>
          <div className="task-property">{task.property_address}</div>
        </div>
        <div className="task-badges">
          <Badge type={getPriorityType(task.priority)}>{task.priority}</Badge>
          <Badge type={getStatusType(task.status)}>{task.status}</Badge>
        </div>
      </div>
      
      <div className="task-description">{task.description}</div>
      
      <div className="task-details">
        <div className="task-detail">
          <div className="task-detail-label">Category</div>
          <div className="task-detail-value">{task.category}</div>
        </div>
        <div className="task-detail">
          <div className="task-detail-label">Due Date</div>
          <div className="task-detail-value">{formatDate(task.due_date)}</div>
        </div>
        <div className="task-detail">
          <div className="task-detail-label">Est. Cost</div>
          <div className="task-detail-value">{formatCurrency(task.estimated_cost)}</div>
        </div>
        <div className="task-detail">
          <div className="task-detail-label">Emergency Cost</div>
          <div className="task-detail-value">{formatCurrency(task.emergency_cost_if_delayed)}</div>
        </div>
        {task.status !== 'Completed' && (
          <div className="task-detail">
            <div className="task-detail-label">Time Left</div>
            <div className="task-detail-value">{getDaysUntilDue(task.due_date, task.status)}</div>
          </div>
        )}
      </div>
      
      <div className="task-actions">
        {task.status !== 'Completed' && (
          <Button 
            variant="success" 
            size="sm" 
            onClick={() => onUpdate(task.id, { status: 'Completed', completed_date: new Date().toISOString().split('T')[0] })}
            icon={Icons.CheckCircle}
          >
            Complete
          </Button>
        )}
        <Button 
          variant="secondary" 
          size="sm" 
          onClick={() => onUpdate(task.id, task)}
          icon={Icons.Edit}
        >
          Edit
        </Button>
        <Button 
          variant="danger" 
          size="sm" 
          onClick={() => onDelete(task.id)}
          icon={Icons.Trash}
        >
          Delete
        </Button>
      </div>
    </div>
  );
};

const TaskForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    property_address: '',
    task_name: '',
    description: '',
    category: 'HVAC',
    priority: 'Medium',
    due_date: '',
    estimated_cost: 0,
    emergency_cost_if_delayed: 0,
    notes: ''
  });

  const categories = ['HVAC', 'Plumbing', 'Electrical', 'Roofing', 'Flooring', 'Windows', 'Appliances', 'Exterior', 'Landscaping', 'Safety', 'Other'];
  const priorities = ['High', 'Medium', 'Low'];

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({
      property_address: '',
      task_name: '',
      description: '',
      category: 'HVAC',
      priority: 'Medium',
      due_date: '',
      estimated_cost: 0,
      emergency_cost_if_delayed: 0,
      notes: ''
    });
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Add New Maintenance Task</h3>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">Property Address</label>
            <input
              type="text"
              className="form-input"
              value={formData.property_address}
              onChange={(e) => setFormData({ ...formData, property_address: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Task Name</label>
            <input
              type="text"
              className="form-input"
              value={formData.task_name}
              onChange={(e) => setFormData({ ...formData, task_name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Category</label>
            <select
              className="form-select"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Priority</label>
            <select
              className="form-select"
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
            >
              {priorities.map(pri => (
                <option key={pri} value={pri}>{pri}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Due Date</label>
            <input
              type="date"
              className="form-input"
              value={formData.due_date}
              onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Estimated Cost ($)</label>
            <input
              type="number"
              className="form-input"
              value={formData.estimated_cost}
              onChange={(e) => setFormData({ ...formData, estimated_cost: parseFloat(e.target.value) || 0 })}
              min="0"
              step="0.01"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Emergency Cost if Delayed ($)</label>
            <input
              type="number"
              className="form-input"
              value={formData.emergency_cost_if_delayed}
              onChange={(e) => setFormData({ ...formData, emergency_cost_if_delayed: parseFloat(e.target.value) || 0 })}
              min="0"
              step="0.01"
            />
          </div>
        </div>
        <div className="form-group">
          <label className="form-label">Description</label>
          <textarea
            className="form-input"
            rows="3"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            required
          />
        </div>
        <div className="form-group">
          <label className="form-label">Notes</label>
          <textarea
            className="form-input"
            rows="2"
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          />
        </div>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '2rem' }}>
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" icon={Icons.Plus}>
            Create Task
          </Button>
        </div>
      </form>
    </div>
  );
};

function App() {
  const [stats, setStats] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    category: '',
    priority: ''
  });

  // API Functions
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      } else {
        throw new Error(data.error || 'Failed to fetch stats');
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError('Failed to load dashboard statistics');
    }
  };

  const fetchTasks = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.category) params.append('category', filters.category);
      if (filters.priority) params.append('priority', filters.priority);
      
      const response = await fetch(`${API_BASE_URL}/tasks?${params}`);
      if (!response.ok) throw new Error('Failed to fetch tasks');
      
      const data = await response.json();
      setTasks(data);
    } catch (err) {
      console.error('Error fetching tasks:', err);
      setError('Failed to load tasks');
    }
  };

  const createTask = async (taskData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData)
      });
      
      if (!response.ok) throw new Error('Failed to create task');
      
      setShowForm(false);
      fetchTasks();
      fetchStats();
    } catch (err) {
      console.error('Error creating task:', err);
      setError('Failed to create task');
    }
  };

  const updateTask = async (taskId, updateData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });
      
      if (!response.ok) throw new Error('Failed to update task');
      
      fetchTasks();
      fetchStats();
    } catch (err) {
      console.error('Error updating task:', err);
      setError('Failed to update task');
    }
  };

  const deleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Failed to delete task');
      
      fetchTasks();
      fetchStats();
    } catch (err) {
      console.error('Error deleting task:', err);
      setError('Failed to delete task');
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchTasks()]);
      setLoading(false);
    };
    
    loadData();
  }, [filters]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  if (loading) {
    return (
      <div className="app-container">
        <div className="loading">
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⏳</div>
            <div>Loading Property Maintenance Tracker...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <Icons.Home />
            <h1>Property Maintenance Tracker</h1>
          </div>
          <Button 
            variant="primary" 
            onClick={() => setShowForm(!showForm)}
            icon={Icons.Plus}
          >
            {showForm ? 'Cancel' : 'Add Task'}
          </Button>
        </div>
      </header>

      <main className="main-content">
        {error && (
          <div className="error">
            <strong>Error:</strong> {error}
            <button 
              style={{ float: 'right', background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer' }}
              onClick={() => setError(null)}
            >
              ×
            </button>
          </div>
        )}

        {/* Dashboard Statistics */}
        {stats && (
          <div className="stats-grid">
            <StatCard
              title="Total Tasks"
              value={stats.total_tasks}
              icon={Icons.Tools}
              type="default"
            />
            <StatCard
              title="Pending Tasks"
              value={stats.pending}
              icon={Icons.Clock}
              type="warning"
            />
            <StatCard
              title="Overdue Tasks"
              value={stats.overdue}
              icon={Icons.AlertTriangle}
              type="danger"
            />
            <StatCard
              title="Completed Tasks"
              value={stats.completed}
              icon={Icons.CheckCircle}
              type="success"
            />
            <StatCard
              title="Preventive Cost"
              value={formatCurrency(stats.preventive_cost)}
              icon={Icons.DollarSign}
              type="default"
            />
            <StatCard
              title="Emergency Cost Averted"
              value={formatCurrency(stats.emergency_cost_averted)}
              icon={Icons.TrendingUp}
              type="success"
            />
            <StatCard
              title="Net Savings"
              value={formatCurrency(stats.net_savings)}
              icon={Icons.TrendingUp}
              type={stats.net_savings >= 0 ? "success" : "danger"}
            />
          </div>
        )}

        {/* Add Task Form */}
        {showForm && (
          <div style={{ marginBottom: '2rem' }}>
            <TaskForm 
              onSubmit={createTask}
              onCancel={() => setShowForm(false)}
            />
          </div>
        )}

        {/* Task List */}
        <div className="task-list">
          <div className="task-header">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 className="card-title">Maintenance Tasks</h2>
              <Icons.Filter />
            </div>
            <div className="task-filters">
              <div className="form-group">
                <select
                  className="form-select"
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                >
                  <option value="">All Statuses</option>
                  <option value="Pending">Pending</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Completed">Completed</option>
                  <option value="Overdue">Overdue</option>
                </select>
              </div>
              <div className="form-group">
                <select
                  className="form-select"
                  value={filters.category}
                  onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                >
                  <option value="">All Categories</option>
                  <option value="HVAC">HVAC</option>
                  <option value="Plumbing">Plumbing</option>
                  <option value="Electrical">Electrical</option>
                  <option value="Roofing">Roofing</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="form-group">
                <select
                  className="form-select"
                  value={filters.priority}
                  onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                >
                  <option value="">All Priorities</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>
            </div>
          </div>
          
          {tasks.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: '#6b7280' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📋</div>
              <div>No maintenance tasks found</div>
              <div style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
                {showForm ? 'Fill out the form above to create your first task' : 'Click "Add Task" to get started'}
              </div>
            </div>
          ) : (
            tasks.map(task => (
              <TaskItem
                key={task.id}
                task={task}
                onUpdate={updateTask}
                onDelete={deleteTask}
              />
            ))
          )}
        </div>
      </main>
    </div>
  );
}

export default App;