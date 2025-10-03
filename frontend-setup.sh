#!/bin/bash
# Frontend setup for Amazon Linux 2023

# Update system
sudo dnf update -y

# Install Nginx
sudo dnf install -y nginx

# Start and enable Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Create frontend directory
sudo mkdir -p /var/www/cloud-notebook
sudo chown -R nginx:nginx /var/www/cloud-notebook

# Backend host (your actual backend instance)
BACKEND_HOST="ec2-54-87-53-238.compute-1.amazonaws.com"

# Create the frontend HTML file
sudo cat > /var/www/cloud-notebook/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Notebook</title>
    <style>
        :root {
            --primary-color: #4a6fa5;
            --secondary-color: #6b8cbc;
            --accent-color: #ff7e5f;
            --light-color: #f8f9fa;
            --dark-color: #343a40;
            --success-color: #28a745;
            --danger-color: #dc3545;
            --border-radius: 8px;
            --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --transition: all 0.3s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: #f5f7fa;
            color: var(--dark-color);
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        header {
            background-color: var(--primary-color);
            color: white;
            padding: 1rem 0;
            box-shadow: var(--box-shadow);
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: bold;
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.9rem;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: var(--success-color);
        }

        .status-dot.offline {
            background-color: var(--danger-color);
        }

        main {
            padding: 2rem 0;
            min-height: calc(100vh - 140px);
        }

        .dashboard {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 2rem;
        }

        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
        }

        .notes-sidebar {
            background-color: white;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 1.5rem;
            height: fit-content;
        }

        .notes-list {
            max-height: 500px;
            overflow-y: auto;
        }

        .note-item {
            padding: 1rem;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            transition: var(--transition);
        }

        .note-item:hover {
            background-color: #f8f9fa;
        }

        .note-item.active {
            background-color: #e9ecef;
            border-left: 4px solid var(--primary-color);
        }

        .note-title {
            font-weight: bold;
            margin-bottom: 0.5rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .note-preview {
            font-size: 0.9rem;
            color: #6c757d;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .note-date {
            font-size: 0.8rem;
            color: #adb5bd;
            margin-top: 0.5rem;
        }

        .editor-container {
            background-color: white;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            height: 600px;
        }

        .editor-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #eee;
        }

        .editor-title {
            width: 100%;
            border: none;
            font-size: 1.5rem;
            font-weight: bold;
            padding: 0.5rem 0;
            margin-bottom: 1rem;
            border-bottom: 2px solid transparent;
        }

        .editor-title:focus {
            outline: none;
            border-bottom: 2px solid var(--primary-color);
        }

        .editor-content {
            flex: 1;
            border: none;
            resize: none;
            font-size: 1rem;
            line-height: 1.6;
            padding: 0.5rem;
            border-radius: var(--border-radius);
            background-color: #f8f9fa;
        }

        .editor-content:focus {
            outline: none;
            background-color: white;
            box-shadow: 0 0 0 2px rgba(74, 111, 165, 0.2);
        }

        .editor-actions {
            display: flex;
            justify-content: flex-end;
            gap: 1rem;
            margin-top: 1rem;
        }

        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: var(--border-radius);
            cursor: pointer;
            font-weight: bold;
            transition: var(--transition);
        }

        .btn-primary {
            background-color: var(--primary-color);
            color: white;
        }

        .btn-primary:hover {
            background-color: var(--secondary-color);
        }

        .btn-danger {
            background-color: var(--danger-color);
            color: white;
        }

        .btn-danger:hover {
            background-color: #c82333;
        }

        .btn-success {
            background-color: var(--success-color);
            color: white;
        }

        .btn-success:hover {
            background-color: #218838;
        }

        .btn-outline {
            background-color: transparent;
            border: 1px solid var(--primary-color);
            color: var(--primary-color);
        }

        .btn-outline:hover {
            background-color: var(--primary-color);
            color: white;
        }

        .stats-container {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background-color: white;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 1.5rem;
            flex: 1;
            text-align: center;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }

        .stat-label {
            color: #6c757d;
            font-size: 0.9rem;
        }

        .empty-state {
            text-align: center;
            padding: 2rem;
            color: #6c757d;
        }

        .empty-state i {
            font-size: 3rem;
            margin-bottom: 1rem;
            color: #adb5bd;
        }

        .loading {
            text-align: center;
            padding: 2rem;
        }

        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-left-color: var(--primary-color);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }

        .alert {
            padding: 1rem;
            border-radius: var(--border-radius);
            margin-bottom: 1rem;
        }

        .alert-success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .alert-error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        footer {
            background-color: var(--dark-color);
            color: white;
            text-align: center;
            padding: 1rem 0;
            margin-top: 2rem;
        }

        .search-box {
            margin-bottom: 1rem;
        }

        .search-input {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: var(--border-radius);
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">📓 Cloud Notebook</div>
                <div class="status-indicator">
                    <span>Database Status:</span>
                    <div class="status-dot" id="statusDot"></div>
                    <span id="statusText">Checking...</span>
                </div>
            </div>
        </div>
    </header>

    <main class="container">
        <div class="stats-container" id="statsContainer">
            <!-- Stats will be loaded here -->
        </div>

        <div id="alertContainer"></div>

        <div class="dashboard">
            <div class="notes-sidebar">
                <div class="search-box">
                    <input type="text" class="search-input" id="searchInput" placeholder="Search notes...">
                </div>
                <div class="notes-list" id="notesList">
                    <!-- Notes will be loaded here -->
                </div>
                <button class="btn btn-primary" id="newNoteBtn" style="width: 100%; margin-top: 1rem;">
                    + New Note
                </button>
            </div>

            <div class="editor-container">
                <div class="editor-header">
                    <h3 id="editorTitle">Select a note or create a new one</h3>
                    <div class="editor-actions" id="editorActions" style="display: none;">
                        <button class="btn btn-danger" id="deleteNoteBtn">Delete</button>
                        <button class="btn btn-outline" id="cancelEditBtn">Cancel</button>
                        <button class="btn btn-success" id="saveNoteBtn">Save</button>
                    </div>
                </div>
                <input type="text" class="editor-title" id="noteTitle" placeholder="Note title" style="display: none;">
                <textarea class="editor-content" id="noteContent" placeholder="Start writing your note here..." style="display: none;"></textarea>
                <div id="emptyEditor" class="empty-state">
                    <div>📝</div>
                    <h3>No note selected</h3>
                    <p>Select a note from the list or create a new one to start editing.</p>
                </div>
            </div>
        </div>
    </main>

    <footer>
        <div class="container">
            <p>Cloud Notebook &copy; 2023 | Powered by Amazon RDS MySQL | Backend: ec2-54-87-53-238.compute-1.amazonaws.com:5054</p>
        </div>
    </footer>

    <script>
        // API Configuration - Point to Your Backend EC2
        const API_BASE_URL = 'http://ec2-54-87-53-238.compute-1.amazonaws.com:5054';

        // Global state
        let currentNoteId = null;
        let notes = [];
        let originalNote = {};

        // DOM Elements
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        const statsContainer = document.getElementById('statsContainer');
        const alertContainer = document.getElementById('alertContainer');
        const notesList = document.getElementById('notesList');
        const searchInput = document.getElementById('searchInput');
        const newNoteBtn = document.getElementById('newNoteBtn');
        const editorTitle = document.getElementById('editorTitle');
        const noteTitle = document.getElementById('noteTitle');
        const noteContent = document.getElementById('noteContent');
        const editorActions = document.getElementById('editorActions');
        const emptyEditor = document.getElementById('emptyEditor');
        const saveNoteBtn = document.getElementById('saveNoteBtn');
        const cancelEditBtn = document.getElementById('cancelEditBtn');
        const deleteNoteBtn = document.getElementById('deleteNoteBtn');

        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            checkHealth();
            loadStats();
            loadNotes();
            setupEventListeners();
        });

        // Set up event listeners
        function setupEventListeners() {
            newNoteBtn.addEventListener('click', createNewNote);
            saveNoteBtn.addEventListener('click', saveNote);
            cancelEditBtn.addEventListener('click', cancelEdit);
            deleteNoteBtn.addEventListener('click', deleteNote);
            searchInput.addEventListener('input', filterNotes);
            
            // Auto-save on content change (with debounce)
            let saveTimeout;
            noteTitle.addEventListener('input', () => {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(saveNote, 2000);
            });
            
            noteContent.addEventListener('input', () => {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(saveNote, 2000);
            });
        }

        // Check API health
        async function checkHealth() {
            try {
                const response = await fetch(`${API_BASE_URL}/health`);
                const data = await response.json();
                
                if (data.status === 'healthy') {
                    statusDot.classList.remove('offline');
                    statusText.textContent = 'Connected to RDS MySQL';
                } else {
                    statusDot.classList.add('offline');
                    statusText.textContent = 'Database connection issue';
                }
            } catch (error) {
                console.error('Health check failed:', error);
                statusDot.classList.add('offline');
                statusText.textContent = 'Connection failed';
            }
        }

        // Load statistics
        async function loadStats() {
            try {
                const response = await fetch(`${API_BASE_URL}/stats`);
                const data = await response.json();
                
                statsContainer.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-value">${data.total_notes}</div>
                        <div class="stat-label">Total Notes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.recent_notes_24h}</div>
                        <div class="stat-label">Recent (24h)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">RDS</div>
                        <div class="stat-label">Database</div>
                    </div>
                `;
            } catch (error) {
                console.error('Failed to load stats:', error);
                statsContainer.innerHTML = '<div class="alert alert-error">Failed to load statistics</div>';
            }
        }

        // Load all notes
        async function loadNotes() {
            try {
                notesList.innerHTML = '<div class="loading"><div class="spinner"></div>Loading notes...</div>';
                
                const response = await fetch(`${API_BASE_URL}/notes`);
                notes = await response.json();
                
                renderNotes(notes);
            } catch (error) {
                console.error('Failed to load notes:', error);
                notesList.innerHTML = '<div class="alert alert-error">Failed to load notes</div>';
            }
        }

        // Render notes in the sidebar
        function renderNotes(notesToRender) {
            if (notesToRender.length === 0) {
                notesList.innerHTML = `
                    <div class="empty-state">
                        <div>📝</div>
                        <p>No notes yet. Create your first note!</p>
                    </div>
                `;
                return;
            }
            
            notesList.innerHTML = notesToRender.map(note => `
                <div class="note-item ${currentNoteId === note.id ? 'active' : ''}" data-id="${note.id}">
                    <div class="note-title">${note.title || 'Untitled Note'}</div>
                    <div class="note-preview">${note.content ? note.content.substring(0, 100) : 'No content'}</div>
                    <div class="note-date">${formatDate(note.updated_at)}</div>
                </div>
            `).join('');
            
            // Add click event to each note item
            document.querySelectorAll('.note-item').forEach(item => {
                item.addEventListener('click', () => {
                    const noteId = parseInt(item.getAttribute('data-id'));
                    selectNote(noteId);
                });
            });
        }

        // Filter notes based on search input
        function filterNotes() {
            const searchTerm = searchInput.value.toLowerCase();
            const filteredNotes = notes.filter(note => 
                note.title.toLowerCase().includes(searchTerm) || 
                note.content.toLowerCase().includes(searchTerm)
            );
            renderNotes(filteredNotes);
        }

        // Select a note for editing
        async function selectNote(noteId) {
            try {
                const response = await fetch(`${API_BASE_URL}/notes/${noteId}`);
                const note = await response.json();
                
                // Update UI to show editor
                emptyEditor.style.display = 'none';
                noteTitle.style.display = 'block';
                noteContent.style.display = 'block';
                editorActions.style.display = 'flex';
                
                // Set note content
                noteTitle.value = note.title || '';
                noteContent.value = note.content || '';
                currentNoteId = noteId;
                
                // Store original values for cancel
                originalNote = {
                    title: note.title || '',
                    content: note.content || ''
                };
                
                // Update active state in list
                document.querySelectorAll('.note-item').forEach(item => {
                    item.classList.remove('active');
                    if (parseInt(item.getAttribute('data-id')) === noteId) {
                        item.classList.add('active');
                    }
                });
                
                // Update editor title
                editorTitle.textContent = 'Editing Note';
            } catch (error) {
                console.error('Failed to load note:', error);
                showAlert('Failed to load note', 'error');
            }
        }

        // Create a new note
        function createNewNote() {
            // Reset editor
            emptyEditor.style.display = 'none';
            noteTitle.style.display = 'block';
            noteContent.style.display = 'block';
            editorActions.style.display = 'flex';
            
            // Clear fields
            noteTitle.value = '';
            noteContent.value = '';
            currentNoteId = null;
            
            // Store original values (empty)
            originalNote = {
                title: '',
                content: ''
            };
            
            // Update editor title
            editorTitle.textContent = 'New Note';
            
            // Focus on title field
            noteTitle.focus();
        }

        // Save note (create or update)
        async function saveNote() {
            const title = noteTitle.value.trim();
            const content = noteContent.value.trim();
            
            // Validate
            if (!title) {
                showAlert('Note title is required', 'error');
                return;
            }
            
            try {
                let response;
                
                if (currentNoteId) {
                    // Update existing note
                    response = await fetch(`${API_BASE_URL}/notes/${currentNoteId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            title: title,
                            content: content
                        })
                    });
                } else {
                    // Create new note
                    response = await fetch(`${API_BASE_URL}/notes`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            title: title,
                            content: content
                        })
                    });
                }
                
                if (response.ok) {
                    showAlert(`Note ${currentNoteId ? 'updated' : 'created'} successfully`, 'success');
                    
                    // Reload notes and stats
                    loadNotes();
                    loadStats();
                    
                    // If it was a new note, we need to get its ID
                    if (!currentNoteId) {
                        const data = await response.json();
                        currentNoteId = data.id;
                    }
                    
                    // Update original values
                    originalNote = {
                        title: title,
                        content: content
                    };
                } else {
                    throw new Error('Failed to save note');
                }
            } catch (error) {
                console.error('Failed to save note:', error);
                showAlert('Failed to save note', 'error');
            }
        }

        // Cancel editing
        function cancelEdit() {
            // Restore original values
            noteTitle.value = originalNote.title;
            noteContent.value = originalNote.content;
            
            // If we were creating a new note, clear the editor
            if (!currentNoteId) {
                resetEditor();
            }
        }

        // Delete current note
        async function deleteNote() {
            if (!currentNoteId) return;
            
            if (!confirm('Are you sure you want to delete this note?')) {
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/notes/${currentNoteId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    showAlert('Note deleted successfully', 'success');
                    resetEditor();
                    loadNotes();
                    loadStats();
                } else {
                    throw new Error('Failed to delete note');
                }
            } catch (error) {
                console.error('Failed to delete note:', error);
                showAlert('Failed to delete note', 'error');
            }
        }

        // Reset editor to empty state
        function resetEditor() {
            emptyEditor.style.display = 'block';
            noteTitle.style.display = 'none';
            noteContent.style.display = 'none';
            editorActions.style.display = 'none';
            
            noteTitle.value = '';
            noteContent.value = '';
            currentNoteId = null;
            originalNote = {};
            
            editorTitle.textContent = 'Select a note or create a new one';
            
            // Clear active state in list
            document.querySelectorAll('.note-item').forEach(item => {
                item.classList.remove('active');
            });
        }

        // Show alert message
        function showAlert(message, type) {
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            
            alertContainer.appendChild(alert);
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }

        // Format date for display
        function formatDate(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);
            
            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins} min ago`;
            if (diffHours < 24) return `${diffHours} hr ago`;
            if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
            
            return date.toLocaleDateString();
        }
    </script>
</body>
</html>
EOF

# Configure Nginx
sudo cat > /etc/nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 4096;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    server {
        listen       80;
        listen       [::]:80;
        server_name  _;
        root         /var/www/cloud-notebook;

        # Frontend
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://ec2-54-87-53-238.compute-1.amazonaws.com:5054/health;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Configure firewall
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

echo "✅ Frontend setup complete!"
echo "🌐 Frontend URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "🔗 Backend: ec2-54-87-53-238.compute-1.amazonaws.com:5054"