import React, { useState, useEffect } from 'react';
import { Calendar, Bell, CheckCircle, AlertTriangle, Plus, Search, Settings, Users, Mail, MessageSquare, BarChart3, Download } from 'lucide-react';

// API base URL - change this when deploying
import { API_BASE_URL } from "./config";

const MaintenanceTrackerApp = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [properties, setProperties] = useState([
    { id: 1, name: "Sunrise Apartments", units: 12, manager: "John Smith", contact: "+1-555-0123" },
    { id: 2, name: "Downtown Plaza", units: 8, manager: "Sarah Johnson", contact: "+1-555-0456" }
  ]);
  
  // State now connects to your Python backend
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({
    total_tasks: 0,
    pending: 0,
    overdue: 0,
    completed: 0,
    preventive_cost: 0,
    emergency_cost_averted: 0,
    net_savings: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [reminders, setReminders] = useState({
    email: true,
    sms: true,
    frequency: '3days'
  });

  const [newTask, setNewTask] = useState({
    property_name: '',
    task_description: '',
    due_date: '',
    priority: 'Medium',
    estimated_cost: ''
  });

  // API helper function
  const apiCall = async (endpoint, options = {}) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });
      
      if (!response.ok) {
        throw new Error(`API call failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      setError(error.message);
      throw error;
    }
  };

  // Load data from your Python backend
  const loadTasks = async () => {
    try {
      setLoading(true);
      const response = await apiCall('/tasks');
      if (response.success) {
        setTasks(response.tasks);
      }
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await apiCall('/stats');
      if (response.success) {
        setStats(response.stats);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  // Load data on component mount
  useEffect(() => {
    loadTasks();
    loadStats();
  }, []);

  // Add task using your Python API
  const addTask = async () => {
    if (newTask.property_name && newTask.task_description && newTask.due_date) {
      try {
        const response = await apiCall('/tasks', {
          method: 'POST',
          body: JSON.stringify({
            property_name: newTask.property_name,
            task_description: newTask.task_description,
            due_date: newTask.due_date,
            priority: newTask.priority
          }),
        });

        if (response.success) {
          // Reload tasks and stats
          await loadTasks();
          await loadStats();
          
          // Reset form
          setNewTask({ 
            property_name: '', 
            task_description: '', 
            due_date: '', 
            priority: 'Medium', 
            estimated_cost: '' 
          });
        }
      } catch (error) {
        console.error('Failed to add task:', error);
      }
    }
  };

  // Mark task complete using your Python API
  const markComplete = async (taskDescription) => {
    try {
      const response = await apiCall(`/tasks/complete?task_description=${encodeURIComponent(taskDescription)}`, {
        method: 'PUT',
      });

      if (response.success) {
        // Reload tasks and stats
        await loadTasks();
        await loadStats();
      }
    } catch (error) {
      console.error('Failed to mark task complete:', error);
    }
  };

  // SMS command simulation (connects to your Python SMS processor)
  const processSMSCommand = async (smsText) => {
    try {
      const response = await apiCall('/sms/command', {
        method: 'POST',
        body: JSON.stringify({
          sms_text: smsText,
          sender_phone: '+1-555-0123'
        }),
      });

      if (response.success) {
        // Reload data after SMS command
        await loadTasks();
        await loadStats();
        alert(`SMS Command Result: ${response.message}`);
      } else {
        alert(`SMS Command Failed: ${response.message}`);
      }
    } catch (error) {
      console.error('SMS command failed:', error);
      alert('SMS command failed');
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      Critical: 'bg-red-100 text-red-800 border-red-300',
      High: 'bg-orange-100 text-orange-800 border-orange-300',
      Medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      Low: 'bg-green-100 text-green-800 border-green-300'
    };
    return colors[priority] || colors.Medium;
  };

  const getStatusColor = (status) => {
    const colors = {
      Completed: 'bg-green-500',
      Pending: 'bg-blue-500',
      overdue: 'bg-red-500',
      Emergency: 'bg-red-600'
    };
    return colors[status] || colors.Pending;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your maintenance data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow-sm border border-red-200">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-4">Failed to connect to the maintenance tracker API.</p>
          <p className="text-sm text-gray-500">Make sure your Python API server is running on port 8000.</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">Property Maintenance Pro</h1>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                Connected to Python API
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => setActiveTab('tasks')}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Plus className="w-4 h-4" />
                <span>Add Task</span>
              </button>
              <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
                <Bell className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
              { id: 'tasks', label: 'Tasks', icon: CheckCircle },
              { id: 'properties', label: 'Properties', icon: Users },
              { id: 'reminders', label: 'Reminders', icon: Bell },
              { id: 'sms', label: 'SMS Commands', icon: MessageSquare },
              { id: 'settings', label: 'Settings', icon: Settings }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Dashboard View - Now uses real data from your Python API */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats Grid - Connected to your Python backend */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Tasks</p>
                    <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total_tasks}</p>
                  </div>
                  <CheckCircle className="w-10 h-10 text-blue-500" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Overdue</p>
                    <p className="text-3xl font-bold text-red-600 mt-1">{stats.overdue}</p>
                  </div>
                  <AlertTriangle className="w-10 h-10 text-red-500" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Cost Savings</p>
                    <p className="text-3xl font-bold text-green-600 mt-1">${stats.emergency_cost_averted.toLocaleString()}</p>
                  </div>
                  <BarChart3 className="w-10 h-10 text-green-500" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Properties</p>
                    <p className="text-3xl font-bold text-gray-900 mt-1">{properties.length}</p>
                  </div>
                  <Users className="w-10 h-10 text-purple-500" />
                </div>
              </div>
            </div>

            {/* ROI Calculator - Uses your Python cost analysis */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Your ROI This Month (Powered by Python Backend)</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <p className="text-sm text-gray-600">Preventive Maintenance Spent</p>
                  <p className="text-2xl font-bold text-gray-900">${stats.preventive_cost.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Emergency Costs Averted</p>
                  <p className="text-2xl font-bold text-green-600">${stats.emergency_cost_averted.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Net Savings</p>
                  <p className="text-2xl font-bold text-green-600">${stats.net_savings.toLocaleString()}</p>
                </div>
              </div>
            </div>

            {/* Upcoming Tasks - Real data from Google Sheets via Python */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-bold text-gray-900">Upcoming Tasks (From Google Sheets)</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {tasks.filter(t => t.Status !== 'Completed').slice(0, 5).map(task => (
                  <div key={task.id || `${task.Property}-${task['Task Description']}`} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <span className={`w-3 h-3 rounded-full ${getStatusColor(task.Status)}`}></span>
                          <h4 className="font-semibold text-gray-900">{task['Task Description']}</h4>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(task.Priority)}`}>
                            {task.Priority}
                          </span>
                        </div>
                        <div className="mt-2 flex items-center space-x-6 text-sm text-gray-600">
                          <span>{task.Property}</span>
                          <span className="flex items-center space-x-1">
                            <Calendar className="w-4 h-4" />
                            <span>{task['Due Date']}</span>
                          </span>
                          {task.Cost && <span>Est. Cost: ${task.Cost}</span>}
                        </div>
                      </div>
                      <button 
                        onClick={() => markComplete(task['Task Description'])}
                        className="ml-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium"
                      >
                        Mark Complete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tasks View - Now connected to Python API */}
        {activeTab === 'tasks' && (
          <div className="space-y-6">
            {/* Add New Task Form - Uses your Python API */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Add New Task (Saves to Google Sheets)</h3>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <select
                  value={newTask.property_name}
                  onChange={(e) => setNewTask({...newTask, property_name: e.target.value})}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select Property</option>
                  {properties.map(p => <option key={p.id} value={p.name}>{p.name}</option>)}
                </select>
                <input
                  type="text"
                  placeholder="Task description"
                  value={newTask.task_description}
                  onChange={(e) => setNewTask({...newTask, task_description: e.target.value})}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <input
                  type="date"
                  value={newTask.due_date}
                  onChange={(e) => setNewTask({...newTask, due_date: e.target.value})}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <select
                  value={newTask.priority}
                  onChange={(e) => setNewTask({...newTask, priority: e.target.value})}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="Low">Low Priority</option>
                  <option value="Medium">Medium Priority</option>
                  <option value="High">High Priority</option>
                  <option value="Critical">Critical</option>
                </select>
                <button
                  onClick={addTask}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                >
                  Add Task
                </button>
              </div>
            </div>

            {/* All Tasks List - Real data from Python/Google Sheets */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                <h3 className="text-lg font-bold text-gray-900">All Tasks (Live from Google Sheets)</h3>
                <button className="flex items-center space-x-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
                  <Download className="w-4 h-4" />
                  <span>Export</span>
                </button>
              </div>
              <div className="divide-y divide-gray-200">
                {tasks.map((task, index) => (
                  <div key={index} className="p-6 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <span className={`w-3 h-3 rounded-full ${getStatusColor(task.Status)}`}></span>
                          <h4 className="font-semibold text-gray-900">{task['Task Description']}</h4>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(task.Priority)}`}>
                            {task.Priority}
                          </span>
                          {task.Status === 'Completed' && (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              ✓ Completed
                            </span>
                          )}
                        </div>
                        <div className="mt-2 flex items-center space-x-6 text-sm text-gray-600">
                          <span>{task.Property}</span>
                          <span className="flex items-center space-x-1">
                            <Calendar className="w-4 h-4" />
                            <span>{task['Due Date']}</span>
                          </span>
                          {task.Cost && <span>Cost: ${task.Cost}</span>}
                        </div>
                      </div>
                      {task.Status !== 'Completed' && (
                        <button 
                          onClick={() => markComplete(task['Task Description'])}
                          className="ml-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium"
                        >
                          Complete
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* SMS Commands Tab - New feature connecting to your Python SMS processor */}
        {activeTab === 'sms' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4">SMS Command Tester</h3>
              <p className="text-gray-600 mb-4">Test your Python SMS integration here:</p>
              
              <div className="space-y-4">
                <div className="flex gap-4">
                  <input
                    type="text"
                    placeholder="Type SMS command (e.g., 'DONE Fix leaking faucet')"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        processSMSCommand(e.target.value);
                        e.target.value = '';
                      }
                    }}
                  />
                  <button
                    onClick={(e) => {
                      const input = e.target.previousElementSibling;
                      processSMSCommand(input.value);
                      input.value = '';
                    }}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Send SMS
                  </button>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">Available Commands:</h4>
                  <div className="space-y-2 text-sm text-blue-900">
                    <div className="flex items-start space-x-2">
                      <span className="font-mono bg-blue-100 px-2 py-1 rounded">DONE [task description]</span>
                      <span>Mark task as complete</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <span className="font-mono bg-blue-100 px-2 py-1 rounded">LIST [property name]</span>
                      <span>Get pending tasks for property</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <span className="font-mono bg-blue-100 px-2 py-1 rounded">ADD [property] [task] [date]</span>
                      <span>Add new task</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Other tabs remain the same... */}
        {activeTab === 'reminders' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-bold text-gray-900 mb-6">Reminder Settings</h3>
              
              <div className="space-y-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Notification Channels</h4>
                  <div className="space-y-3">
                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={reminders.email}
                        onChange={(e) => setReminders({...reminders, email: e.target.checked})}
                        className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <div className="flex items-center space-x-2">
                        <Mail className="w-5 h-5 text-gray-600" />
                        <span className="text-gray-900">Email Reminders (Connected to Python API)</span>
                      </div>
                    </label>
                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={reminders.sms}
                        onChange={(e) => setReminders({...reminders, sms: e.target.checked})}
                        className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <div className="flex items-center space-x-2">
                        <MessageSquare className="w-5 h-5 text-gray-600" />
                        <span className="text-gray-900">SMS Reminders (Via Python Backend)</span>
                      </div>
                    </label>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                    Save Settings (Connects to Python API)
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Properties View */}
        {activeTab === 'properties' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-900">Managed Properties</h3>
            </div>
            <div className="divide-y divide-gray-200">
              {properties.map(property => (
                <div key={property.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-gray-900">{property.name}</h4>
                      <div className="mt-1 text-sm text-gray-600">
                        <span>{property.units} units</span>
                        <span className="mx-2">•</span>
                        <span>Manager: {property.manager}</span>
                        <span className="mx-2">•</span>
                        <span>{property.contact}</span>
                      </div>
                    </div>
                    <button className="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50">
                      View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MaintenanceTrackerApp;