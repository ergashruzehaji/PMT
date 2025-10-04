// Property Management Tracker - Frontend Application
console.log('🏠 PMT: Loading Property Management Tracker v3.0.0...');

const API_BASE_URL = 'https://pmt-production-a984.up.railway.app';
let currentTasks = [];

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('PMT: DOM loaded, initializing...');
    
    // Set last updated time
    document.getElementById('last-updated').textContent = new Date().toLocaleString();
    
    // Initialize app
    initializeApp();
    
    // Set up form submission
    document.getElementById('task-form').addEventListener('submit', handleTaskSubmit);
});

async function initializeApp() {
    await checkAPIHealth();
    await loadDashboardStats();
    await loadTasks();
}

async function checkAPIHealth() {
    try {
        console.log('PMT: Checking API health...');
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        console.log('PMT: API Health Response:', data);
        
        document.getElementById('api-status').innerHTML = 
            `✅ ${data.status || 'Unknown'} (${data.tracker_available ? 'Google Sheets Connected' : 'Demo Mode'})`;
        document.getElementById('storage-type').innerHTML = 
            `📊 ${data.storage_type || 'Unknown'}`;
        
    } catch (error) {
        console.error('PMT: API Health Check Failed:', error);
        document.getElementById('api-status').innerHTML = '❌ Offline';
        document.getElementById('storage-type').innerHTML = '📊 Unavailable';
    }
}

async function loadDashboardStats() {
    try {
        console.log('PMT: Loading dashboard stats...');
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        const data = await response.json();
        
        if (data.success && data.stats) {
            const stats = data.stats;
            document.getElementById('total-tasks').textContent = stats.total_tasks || 0;
            document.getElementById('pending-tasks').textContent = stats.pending || 0;
            document.getElementById('completed-tasks').textContent = stats.completed || 0;
            document.getElementById('cost-savings').textContent = 
                `$${(stats.net_savings || 0).toLocaleString()}`;
            
            console.log('PMT: Stats loaded successfully:', stats);
        } else {
            console.log('PMT: No stats available, using defaults');
        }
    } catch (error) {
        console.error('PMT: Failed to load stats:', error);
    }
}

async function loadTasks() {
    try {
        console.log('PMT: Loading tasks...');
        const response = await fetch(`${API_BASE_URL}/api/tasks`);
        const data = await response.json();
        
        if (data.success && data.tasks) {
            currentTasks = data.tasks;
            renderTasks(currentTasks);
            console.log('PMT: Tasks loaded successfully:', currentTasks.length);
        } else {
            console.log('PMT: No tasks available');
            document.getElementById('tasks-container').innerHTML = '<p>No tasks found.</p>';
        }
    } catch (error) {
        console.error('PMT: Failed to load tasks:', error);
        document.getElementById('tasks-container').innerHTML = '<p>Error loading tasks.</p>';
    }
}

function renderTasks(tasks) {
    const container = document.getElementById('tasks-container');
    
    if (tasks.length === 0) {
        container.innerHTML = '<p>No tasks found. Add a task above to get started!</p>';
        return;
    }
    
    const tasksHTML = tasks.map(task => {
        const priorityClass = task.priority === 'High' ? 'high-priority' : '';
        const statusClass = task.status === 'Completed' ? 'completed' : '';
        
        return `
            <div class="task-item ${priorityClass} ${statusClass}">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h4>${task.task_description || 'Untitled Task'}</h4>
                        <p><strong>Property:</strong> ${task.property_name || 'Unknown'}</p>
                        <p><strong>Due:</strong> ${task.due_date || 'No date'} | 
                           <strong>Priority:</strong> ${task.priority || 'Medium'} | 
                           <strong>Category:</strong> ${task.category || 'General'}</p>
                        <p><strong>Status:</strong> ${task.status || 'Pending'}</p>
                        ${task.estimated_cost ? `<p><strong>Cost:</strong> $${task.estimated_cost}</p>` : ''}
                        ${task.notes ? `<p><strong>Notes:</strong> ${task.notes}</p>` : ''}
                    </div>
                    <div class="task-actions">
                        ${task.status !== 'Completed' ? 
                            `<button class="complete" onclick="completeTask('${task.id}')">✅ Complete</button>` : ''}
                        <button class="delete" onclick="deleteTask('${task.id}')">🗑️ Delete</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = tasksHTML;
}

async function handleTaskSubmit(event) {
    event.preventDefault();
    
    const taskData = {
        property_name: document.getElementById('property-name').value,
        task_description: document.getElementById('task-description').value,
        due_date: document.getElementById('due-date').value,
        priority: document.getElementById('priority').value,
        category: document.getElementById('category').value,
        estimated_cost: parseFloat(document.getElementById('estimated-cost').value) || 0,
        notes: document.getElementById('notes').value
    };
    
    try {
        console.log('PMT: Creating task:', taskData);
        const response = await fetch(`${API_BASE_URL}/api/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Task created successfully!');
            document.getElementById('task-form').reset();
            await loadTasks();
            await loadDashboardStats();
        } else {
            alert('Error creating task: ' + result.message);
        }
    } catch (error) {
        console.error('PMT: Error creating task:', error);
        alert('Error creating task. Please try again.');
    }
}

async function completeTask(taskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                status: 'Completed',
                completed_date: new Date().toISOString().split('T')[0]
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Task completed!');
            await loadTasks();
            await loadDashboardStats();
        } else {
            alert('Error completing task: ' + result.message);
        }
    } catch (error) {
        console.error('PMT: Error completing task:', error);
        alert('Error completing task. Please try again.');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Task deleted!');
            await loadTasks();
            await loadDashboardStats();
        } else {
            alert('Error deleting task: ' + result.message);
        }
    } catch (error) {
        console.error('PMT: Error deleting task:', error);
        alert('Error deleting task. Please try again.');
    }
}

// Global PMT object for external access
window.PMT = {
    API_BASE_URL,
    checkAPIHealth,
    loadDashboardStats,
    loadTasks,
    currentTasks,
    version: '3.0.0'
};

console.log('PMT: Application initialized successfully!');