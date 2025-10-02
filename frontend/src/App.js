import React, { useState, useEffect } from 'react';
import './App.css';
import { API_BASE_URL } from './config';
// import { LanguageProvider, useLanguage, LiveDateTime, LanguageSelector } from './LanguageContext';

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
  Blueprint: () => <span className="text-2xl">📋</span>,
  Menu: () => <span className="text-2xl">☰</span>,
  Close: () => <span className="text-2xl">✕</span>,
  Contact: () => <span className="text-2xl">📞</span>,
  Feedback: () => <span className="text-2xl">💬</span>,
  Law: () => <span className="text-2xl">⚖️</span>,
  Search: () => <span className="text-2xl">🔍</span>,
  Sheets: () => <span className="text-2xl">📊</span>,
  Settings: () => <span className="text-2xl">⚙️</span>,
  Help: () => <span className="text-2xl">❓</span>
};

// Sound Manager
class SoundManager {
  constructor() {
    this.sounds = {};
    this.createSounds();
  }

  createSounds() {
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
      
      oscillator.frequency.setValueAtTime(523, audioContext.currentTime);
      oscillator.frequency.setValueAtTime(659, audioContext.currentTime + 0.1);
      oscillator.frequency.setValueAtTime(784, audioContext.currentTime + 0.2);
      
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

// NYC Building Codes Data
const nycBuildingCodes = [
  { id: 1, title: "NYC Building Code Chapter 1", description: "General provisions for building construction and administration" },
  { id: 2, title: "NYC Building Code Chapter 2", description: "Definitions and abbreviations" },
  { id: 3, title: "NYC Building Code Chapter 3", description: "Use and occupancy classification" },
  { id: 4, title: "NYC Building Code Chapter 4", description: "Special detailed requirements based on use and occupancy" },
  { id: 5, title: "NYC Building Code Chapter 5", description: "General building heights and areas" },
  { id: 6, title: "NYC Building Code Chapter 6", description: "Types of construction" },
  { id: 7, title: "NYC Building Code Chapter 7", description: "Fire and smoke protection features" },
  { id: 8, title: "NYC Building Code Chapter 8", description: "Interior finishes" },
  { id: 9, title: "NYC Building Code Chapter 9", description: "Fire protection systems" },
  { id: 10, title: "NYC Building Code Chapter 10", description: "Means of egress" },
  { id: 11, title: "NYC Housing Maintenance Code", description: "Standards for dwelling maintenance and occupancy" },
  { id: 12, title: "NYC Energy Conservation Code", description: "Energy efficiency requirements for buildings" },
  { id: 13, title: "NYC Plumbing Code", description: "Installation and maintenance of plumbing systems" },
  { id: 14, title: "NYC Mechanical Code", description: "HVAC and mechanical system requirements" },
  { id: 15, title: "NYC Electrical Code", description: "Electrical installation and safety standards" },
  { id: 16, title: "Zoning Resolution", description: "Land use and development regulations" },
  { id: 17, title: "Multiple Dwelling Law", description: "Regulations for apartment buildings and multi-family housing" },
  { id: 18, title: "NYC Fire Code", description: "Fire prevention and safety regulations" },
  { id: 19, title: "NYC Health Code", description: "Public health and safety requirements" },
  { id: 20, title: "Local Law 97 (Climate Mobilization Act)", description: "Building emissions limits and energy efficiency" }
];

const boroughContacts = {
  "Manhattan": { phone: "(212) 393-2000", address: "280 Broadway, New York, NY 10007" },
  "Brooklyn": { phone: "(718) 802-3700", address: "210 Joralemon Street, Brooklyn, NY 11201" },
  "Queens": { phone: "(718) 286-2020", address: "120-55 Queens Boulevard, Kew Gardens, NY 11424" },
  "Bronx": { phone: "(718) 579-6700", address: "1932 Arthur Avenue, Bronx, NY 10457" },
  "Staten Island": { phone: "(718) 390-5100", address: "10 Richmond Terrace, Staten Island, NY 10301" }
};

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

// Left Sidebar Component
const LeftSidebar = ({ onMenuItemClick, isOpen, onClose }) => {
  return (
    <>
      {/* Sidebar Overlay */}
      {isOpen && (
        <div 
          className="sidebar-overlay" 
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <div className={`left-sidebar ${isOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <div className="sidebar-section">
          <div className="sidebar-title">
            <Icons.Menu />
          </div>
          <ul className="sidebar-menu">
            <li className="sidebar-menu-item">
              <div className="sidebar-menu-link" onClick={() => onMenuItemClick('contact')}>
                <Icons.Contact /> Contact
              </div>
            </li>
            <li className="sidebar-menu-item">
              <div className="sidebar-menu-link" onClick={() => onMenuItemClick('feedback')}>
                <Icons.Feedback /> Feedback
              </div>
            </li>
            <li className="sidebar-menu-item">
              <div className="sidebar-menu-link" onClick={() => onMenuItemClick('laws')}>
                <Icons.Law /> Laws & Codes
              </div>
            </li>
            <li className="sidebar-menu-item">
              <div className="sidebar-menu-link" onClick={() => onMenuItemClick('sheets')}>
                <Icons.Sheets /> Sheets
              </div>
            </li>
          </ul>
        </div>
      </div>
    </>
  );
};

// Remove the separate DropdownOverlay component

// Contact Modal Component
const ContactModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2><Icons.Contact /> Contact Information</h2>
          <button className="modal-close" onClick={onClose}><Icons.Close /></button>
        </div>
        <div className="modal-body">
          <div className="contact-info">
            <h3>Property Maintenance Tracker Services</h3>
            <p><strong>Email:</strong> support@propertytracker.com</p>
            <p><strong>Phone:</strong> (555) 123-4567</p>
            <p><strong>Business Hours:</strong> Monday - Friday, 8:00 AM - 6:00 PM EST</p>
            <p><strong>Emergency Line:</strong> (555) 123-HELP (4357)</p>
            <div className="contact-address">
              <h4>Main Office</h4>
              <p>123 Construction Avenue<br/>
              New York, NY 10001<br/>
              United States</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Feedback Modal Component
const FeedbackModal = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    message: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    soundManager.play('success');
    alert('Thank you for your feedback! We will get back to you soon.');
    setFormData({ name: '', email: '', phone: '', message: '' });
    onClose();
  };

  if (!isOpen) return null;
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2><Icons.Feedback /> Feedback Form</h2>
          <button className="modal-close" onClick={onClose}><Icons.Close /></button>
        </div>
        <div className="modal-body">
          <form onSubmit={handleSubmit} className="feedback-form">
            <div className="form-group">
              <label>Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
                placeholder="Your full name"
              />
            </div>
            <div className="form-group">
              <label>Email *</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
                placeholder="your.email@example.com"
              />
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                placeholder="(555) 123-4567"
              />
            </div>
            <div className="form-group">
              <label>Message *</label>
              <textarea
                value={formData.message}
                onChange={(e) => setFormData({...formData, message: e.target.value})}
                required
                rows="5"
                placeholder="Please share your questions, comments, or concerns..."
              />
            </div>
            <div className="form-actions">
              <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
              <Button type="submit" variant="primary">Submit Feedback</Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Laws & Codes Modal Component
const LawsModal = ({ isOpen, onClose }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBorough, setSelectedBorough] = useState('');

  const filteredCodes = nycBuildingCodes.filter(code =>
    code.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    code.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isOpen) return null;
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content large-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2><Icons.Law /> NYC Building Codes & Laws</h2>
          <button className="modal-close" onClick={onClose}><Icons.Close /></button>
        </div>
        <div className="modal-body">
          <div className="search-section">
            <div className="search-bar">
              <Icons.Search />
              <input
                type="text"
                placeholder="Search building codes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          
          <div className="codes-list">
            <h3>NYC Building Codes & Regulations</h3>
            {filteredCodes.map(code => (
              <div key={code.id} className="code-item">
                <h4>{code.title}</h4>
                <p>{code.description}</p>
              </div>
            ))}
          </div>

          <div className="borough-contacts">
            <h3>Department of Buildings Contact Information by Borough</h3>
            <div className="borough-grid">
              {Object.entries(boroughContacts).map(([borough, contact]) => (
                <div key={borough} className="borough-card">
                  <h4>{borough}</h4>
                  <p><strong>Phone:</strong> {contact.phone}</p>
                  <p><strong>Address:</strong> {contact.address}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Sheets Modal Component
const SheetsModal = ({ isOpen, onClose }) => {
  const SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1KdXHj-14FTzbYpFZdA-SZywd_ANWniAgT5lgup_wRTg";
  const EMBED_URL = `${SPREADSHEET_URL}/edit?usp=sharing&rm=embedded&widget=true&headers=false&chrome=false`;

  if (!isOpen) return null;
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content large-modal sheets-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2><Icons.Sheets /> Google Sheets - Property Management Tracker</h2>
          <button className="modal-close" onClick={onClose}><Icons.Close /></button>
        </div>
        <div className="modal-body">
          <div className="sheets-options">
            <div className="sheets-info">
              <h3>📊 Access Your Live Google Sheets</h3>
              <p>View and edit your property maintenance data in real-time. All changes sync automatically with the app.</p>
            </div>
            
            <div className="sheets-actions">
              <a 
                href={SPREADSHEET_URL} 
                target="_blank" 
                rel="noopener noreferrer"
                className="btn btn-primary"
                onClick={() => soundManager.play('success')}
              >
                <Icons.Sheets /> Open in New Tab
              </a>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  navigator.clipboard.writeText(SPREADSHEET_URL);
                  soundManager.play('success');
                  alert('Spreadsheet URL copied to clipboard!');
                }}
              >
                📋 Copy Link
              </button>
            </div>
          </div>

          {/* Embedded Google Sheets */}
          <div className="sheets-embed">
            <h4>📋 Live Spreadsheet Preview</h4>
            <div className="sheets-iframe-container">
              <iframe
                src={EMBED_URL}
                className="sheets-iframe"
                title="Property Management Tracker Spreadsheet"
                frameBorder="0"
                allowFullScreen
              />
            </div>
          </div>

          <div className="sheets-features">
            <h4>✨ Features</h4>
            <div className="feature-grid">
              <div className="feature-item">
                <span className="feature-icon">🔄</span>
                <div>
                  <strong>Real-time Sync</strong>
                  <p>Changes in sheets update the app instantly</p>
                </div>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📱</span>
                <div>
                  <strong>Mobile Friendly</strong>
                  <p>Access from any device, anywhere</p>
                </div>
              </div>
              <div className="feature-item">
                <span className="feature-icon">👥</span>
                <div>
                  <strong>Team Collaboration</strong>
                  <p>Share with team members for collaborative editing</p>
                </div>
              </div>
              <div className="feature-item">
                <span className="feature-icon">💾</span>
                <div>
                  <strong>Auto-Save</strong>
                  <p>Never lose your data with automatic saving</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Edit Task Modal Component
const EditTaskModal = ({ isOpen, onClose, task, onSave }) => {
  const [editData, setEditData] = useState({
    property_name: '',
    task_description: '',
    category: 'General',
    priority: 'Medium',
    due_date: '',
    estimated_cost: 0,
    notes: ''
  });

  useEffect(() => {
    if (task) {
      setEditData({
        property_name: task.property_name || task.property_address || '',
        task_description: task.task_description || task.task_name || '',
        category: task.category || 'General',
        priority: task.priority || 'Medium',
        due_date: task.due_date || '',
        estimated_cost: task.estimated_cost || 0,
        notes: task.notes || task.description || ''
      });
    }
  }, [task]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(task.id, editData);
    onClose();
  };

  if (!isOpen || !task) return null;
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2><Icons.Edit /> Edit Task</h2>
          <button className="modal-close" onClick={onClose}><Icons.Close /></button>
        </div>
        <div className="modal-body">
          <form onSubmit={handleSubmit} className="edit-form">
            <div className="form-grid">
              <div className="form-group">
                <label>Property Name</label>
                <input
                  type="text"
                  value={editData.property_name}
                  onChange={(e) => setEditData({...editData, property_name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Task Description</label>
                <input
                  type="text"
                  value={editData.task_description}
                  onChange={(e) => setEditData({...editData, task_description: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Category</label>
                <select
                  value={editData.category}
                  onChange={(e) => setEditData({...editData, category: e.target.value})}
                >
                  <option value="General">General</option>
                  <option value="HVAC">HVAC</option>
                  <option value="Plumbing">Plumbing</option>
                  <option value="Electrical">Electrical</option>
                  <option value="Roofing">Roofing</option>
                  <option value="Flooring">Flooring</option>
                  <option value="Windows">Windows</option>
                  <option value="Safety">Safety</option>
                </select>
              </div>
              <div className="form-group">
                <label>Priority</label>
                <select
                  value={editData.priority}
                  onChange={(e) => setEditData({...editData, priority: e.target.value})}
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>
              <div className="form-group">
                <label>Due Date</label>
                <input
                  type="date"
                  value={editData.due_date}
                  onChange={(e) => setEditData({...editData, due_date: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Estimated Cost</label>
                <input
                  type="number"
                  value={editData.estimated_cost}
                  onChange={(e) => setEditData({...editData, estimated_cost: parseFloat(e.target.value) || 0})}
                  min="0"
                  step="0.01"
                />
              </div>
            </div>
            <div className="form-group">
              <label>Notes</label>
              <textarea
                value={editData.notes}
                onChange={(e) => setEditData({...editData, notes: e.target.value})}
                rows="3"
              />
            </div>
            <div className="form-actions">
              <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
              <Button type="submit" variant="primary">Save Changes</Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

const TaskItem = ({ task, onUpdate, onDelete, onEdit }) => {
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
    if (!dateString) return 'No date set';
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

  const isOverdue = (dueDate, status) => {
    if (status?.toLowerCase() === 'completed') return false;
    if (!dueDate) return false;
    const today = new Date();
    const due = new Date(dueDate);
    return due < today;
  };

  const getDaysUntilDue = (dueDate, status) => {
    if (status?.toLowerCase() === 'completed') return null;
    if (!dueDate) return 'No due date';
    const today = new Date();
    const due = new Date(dueDate);
    const diffTime = due - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return `${Math.abs(diffDays)} days overdue`;
    if (diffDays === 0) return 'Due today';
    return `${diffDays} days left`;
  };

  const handleComplete = async () => {
    try {
      soundManager.play('success');
      await onUpdate(task.id || task.row_number, { 
        status: 'Completed', 
        completed_date: new Date().toISOString().split('T')[0] 
      });
    } catch (error) {
      console.error('Error completing task:', error);
      // soundManager.play('error'); // Removed error sound
    }
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      // soundManager.play('error'); // Removed error sound
      onDelete(task.id || task.row_number);
    }
  };

  // Use different property name formats for backward compatibility
  const property = task.property_address || task.property_name || task['Property Address'] || task['Property'] || '';
  const taskName = task.task_description || task.task_name || task['Task Description'] || '';
  const description = task.notes || task.description || task['Notes'] || '';
  const category = task.category || task['Category'] || 'General';
  const priority = task.priority || task['Priority'] || 'Medium';
  const status = task.status || task['Status'] || 'Pending';
  const dueDate = task.due_date || task['Due Date'] || '';
  const completedDate = task.completed_date || task['Completed Date'] || '';
  const estimatedCost = task.estimated_cost || task['Estimated Cost'] || 0;
  const emergencyCost = task.emergency_cost || task.emergency_cost_if_delayed || task['Emergency Cost'] || 0;

  const taskIsOverdue = isOverdue(dueDate, status);

  return (
    <div className={`task-item slideIn ${taskIsOverdue ? 'task-overdue' : ''}`}>
      <div className="task-meta">
        <div>
          <div className="task-title">{taskName}</div>
          <div className="task-property">🏠 {property}</div>
        </div>
        <div className="task-badges">
          <Badge type={getPriorityType(priority)}>{priority}</Badge>
          <Badge type={getStatusType(status)}>{status}</Badge>
          {taskIsOverdue && <Badge type="status-overdue">OVERDUE</Badge>}
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
        {status?.toLowerCase() === 'completed' && completedDate && (
          <div className="task-detail">
            <div className="task-detail-label">✅ Completed Date</div>
            <div className="task-detail-value">{formatDate(completedDate)}</div>
          </div>
        )}
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
        {status?.toLowerCase() !== 'completed' && dueDate && (
          <div className="task-detail">
            <div className="task-detail-label">⏰ Time Left</div>
            <div className="task-detail-value">{getDaysUntilDue(dueDate, status)}</div>
          </div>
        )}
      </div>
      
      <div className="task-actions">
        {status?.toLowerCase() !== 'completed' && (
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
          onClick={() => onEdit(task)}
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
    property_name: '',
    task_description: '',
    category: 'General',
    priority: 'Medium',
    due_date: '',
    estimated_cost: 0,
    emergency_cost: 0,
    notes: ''
  });

  const categories = ['General', 'HVAC', 'Plumbing', 'Electrical', 'Roofing', 'Flooring', 'Windows', 'Appliances', 'Exterior', 'Landscaping', 'Safety', 'Other'];
  const priorities = ['High', 'Medium', 'Low'];

  const handleSubmit = (e) => {
    e.preventDefault();
    soundManager.play('success');
    onSubmit(formData);
    setFormData({
      property_name: '',
      task_description: '',
      category: 'General',
      priority: 'Medium',
      due_date: '',
      estimated_cost: 0,
      emergency_cost: 0,
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
            <label className="form-label">🏠 Property Name</label>
            <input
              type="text"
              className="form-input"
              value={formData.property_name}
              onChange={(e) => setFormData({ ...formData, property_name: e.target.value })}
              required
              placeholder="Enter property name"
            />
          </div>
          <div className="form-group">
            <label className="form-label">🔧 Task Description</label>
            <input
              type="text"
              className="form-input"
              value={formData.task_description}
              onChange={(e) => setFormData({ ...formData, task_description: e.target.value })}
              required
              placeholder="Enter task description"
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
          <label className="form-label">📝 Notes</label>
          <textarea
            className="form-input"
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            placeholder="Additional notes or details"
            rows="3"
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
  const [activeModal, setActiveModal] = useState(null);
  const [editingTask, setEditingTask] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Data persistence functions
  const saveToLocalStorage = (tasks) => {
    try {
      localStorage.setItem('pmt_tasks_backup', JSON.stringify(tasks));
      localStorage.setItem('pmt_last_sync', new Date().toISOString());
    } catch (err) {
      console.warn('Failed to save to localStorage:', err);
    }
  };

  const loadFromLocalStorage = () => {
    try {
      const savedTasks = localStorage.getItem('pmt_tasks_backup');
      if (savedTasks) {
        const tasks = JSON.parse(savedTasks);
        const lastSync = localStorage.getItem('pmt_last_sync');
        console.log(`Restored ${tasks.length} tasks from backup (last sync: ${lastSync})`);
        return tasks;
      }
    } catch (err) {
      console.warn('Failed to load from localStorage:', err);
    }
    return [];
  };

  // API Functions
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stats`);
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      } else {
        throw new Error(data.error || 'Failed to fetch stats');
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
      // Set default stats if API fails
      setStats({
        total_tasks: 0,
        pending: 0,
        completed: 0,
        overdue: 0,
        preventive_cost: 0,
        emergency_cost_averted: 0,
        net_savings: 0
      });
      setError('API not available - showing demo mode');
      setTimeout(() => setError(null), 3000);
    }
  };

  const fetchTasks = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.category) params.append('category', filters.category);
      if (filters.priority) params.append('priority', filters.priority);
      
      const response = await fetch(`${API_BASE_URL}/api/tasks?${params}`);
      if (!response.ok) throw new Error('Failed to fetch tasks');
      
      const data = await response.json();
      const fetchedTasks = data.success ? data.tasks : data;
      setTasks(fetchedTasks);
      
      // Save to localStorage as backup
      saveToLocalStorage(fetchedTasks);
      
    } catch (err) {
      console.error('Error fetching tasks:', err);
      
      // Try to restore from localStorage
      const backupTasks = loadFromLocalStorage();
      if (backupTasks.length > 0) {
        setTasks(backupTasks);
        setError(`API unavailable - restored ${backupTasks.length} tasks from backup`);
      } else {
        setTasks([]);
        setError('API not available - tasks will be stored locally');
      }
      setTimeout(() => setError(null), 5000);
    }
  };

  const createTask = async (taskData) => {
    try {
      console.log('Creating task with data:', taskData);
      const response = await fetch(`${API_BASE_URL}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Task creation result:', result);
      
      setShowForm(false);
      setSuccess('Task created successfully!');
      soundManager.play('success');
      setTimeout(() => setSuccess(null), 3000);
      await fetchTasks();
      await fetchStats();
    } catch (err) {
      console.error('Error creating task:', err);
      
      // Fallback: Add task locally when API is not available
      const newTask = {
        id: Date.now().toString(),
        property_name: taskData.property_name || '',
        property_address: taskData.property_name || '',
        task_description: taskData.task_description || '',
        category: taskData.category || 'General',
        priority: taskData.priority || 'Medium',
        status: 'Pending',
        due_date: taskData.due_date || '',
        estimated_cost: taskData.estimated_cost || 0,
        notes: taskData.notes || '',
        created_date: new Date().toISOString().split('T')[0]
      };
      
      // Add to local task list
      setTasks(prevTasks => {
        const updatedTasks = [newTask, ...prevTasks];
        // Save to localStorage as backup
        localStorage.setItem('pmt_tasks_backup', JSON.stringify(updatedTasks));
        return updatedTasks;
      });
      
      // Update stats locally
      setStats(prevStats => ({
        ...prevStats,
        total_tasks: prevStats.total_tasks + 1,
        pending: prevStats.pending + 1,
        preventive_cost: prevStats.preventive_cost + (newTask.estimated_cost || 0)
      }));
      
      setShowForm(false);
      setSuccess('Task created successfully (offline mode)!');
      soundManager.play('success');
      setTimeout(() => setSuccess(null), 3000);
    }
  };

  const updateTask = async (taskId, updateData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });
      
      if (!response.ok) throw new Error('Failed to update task');
      
      setSuccess('Task updated successfully!');
      soundManager.play('success');
      setTimeout(() => setSuccess(null), 3000);
      await fetchTasks();
      await fetchStats();
    } catch (err) {
      console.error('Error updating task:', err);
      
      // Fallback: Update task locally when API is not available
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === taskId ? { ...task, ...updateData } : task
        )
      );
      
      // Update stats if status changed
      if (updateData.status) {
        setStats(prevStats => {
          const updatedStats = { ...prevStats };
          const task = tasks.find(t => t.id === taskId);
          
          if (task && task.status !== updateData.status) {
            // Adjust counts based on status change
            if (task.status === 'Pending') updatedStats.pending--;
            if (task.status === 'Completed') updatedStats.completed--;
            
            if (updateData.status === 'Pending') updatedStats.pending++;
            if (updateData.status === 'Completed') updatedStats.completed++;
          }
          
          return updatedStats;
        });
      }
      
      setSuccess('Task updated successfully (offline mode)!');
      soundManager.play('success');
      setTimeout(() => setSuccess(null), 3000);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Failed to delete task');
      
      setSuccess('Task deleted successfully!');
      setTimeout(() => setSuccess(null), 3000);
      await fetchTasks();
      await fetchStats();
    } catch (err) {
      console.error('Error deleting task:', err);
      
      // Fallback: Delete task locally when API is not available
      const taskToDelete = tasks.find(t => t.id === taskId);
      
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
      
      // Update stats
      if (taskToDelete) {
        setStats(prevStats => ({
          ...prevStats,
          total_tasks: Math.max(0, prevStats.total_tasks - 1),
          pending: taskToDelete.status === 'Pending' ? Math.max(0, prevStats.pending - 1) : prevStats.pending,
          completed: taskToDelete.status === 'Completed' ? Math.max(0, prevStats.completed - 1) : prevStats.completed,
          preventive_cost: Math.max(0, prevStats.preventive_cost - (taskToDelete.estimated_cost || 0))
        }));
      }
      
      setSuccess('Task deleted successfully (offline mode)!');
      setTimeout(() => setSuccess(null), 3000);
    }
  };

  const handleMenuItemClick = (item) => {
    setActiveModal(item);
  };

  const handleEditTask = (task) => {
    setEditingTask(task);
    setActiveModal('edit');
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
          <div className="header-left">
            {/* Hamburger Menu & Navigation Tab */}
            <div className="nav-toggle-container">
              <button 
                className={`nav-toggle ${sidebarOpen ? 'nav-toggle-active' : ''}`}
                onClick={() => setSidebarOpen(!sidebarOpen)}
                title="Toggle Navigation"
              >
                <Icons.Menu />
              </button>
              <div className="nav-tab">
                Navigation
              </div>
            </div>
            
            <div className="header-title">
              <div className="header-icon">
                <Icons.HardHat />
              </div>
              <div>
                <h1>Property Maintenance Tracker</h1>
                <div className="header-subtitle">Professional Construction Management System</div>
              </div>
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

      <LeftSidebar 
        onMenuItemClick={handleMenuItemClick} 
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className={`content-area ${sidebarOpen ? 'content-with-sidebar' : 'content-no-sidebar'}`}>
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
                  <option value="General">General</option>
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
                onEdit={handleEditTask}
              />
            ))
          )}
        </div>
      </main>

      {/* Modals */}
      <ContactModal 
        isOpen={activeModal === 'contact'} 
        onClose={() => setActiveModal(null)} 
      />
      <FeedbackModal 
        isOpen={activeModal === 'feedback'} 
        onClose={() => setActiveModal(null)} 
      />
      <LawsModal 
        isOpen={activeModal === 'laws'} 
        onClose={() => setActiveModal(null)} 
      />
      <SheetsModal 
        isOpen={activeModal === 'sheets'} 
        onClose={() => setActiveModal(null)} 
      />
      <EditTaskModal 
        isOpen={activeModal === 'edit'} 
        onClose={() => setActiveModal(null)}
        task={editingTask}
        onSave={updateTask}
      />
    </div>
  );
}

export default App;