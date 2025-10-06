import json
import boto3
import datetime
import sys
import os

# Try to import pg8000, but provide fallback if not available
try:
    import pg8000
    PG8000_AVAILABLE = True
except ImportError:
    PG8000_AVAILABLE = False
    print("pg8000 not available - running in setup mode")

def lambda_handler(event, context):
    print("=== AWS RDS Notebook ===")
    print("Method:", event.get('httpMethod'))
    print("pg8000 Available:", PG8000_AVAILABLE)
    
    http_method = event.get('httpMethod', 'GET')
    query_params = event.get('queryStringParameters', {}) or {}
    headers = event.get('headers', {}) or {}
    
    # Handle CORS preflight
    if http_method == 'OPTIONS':
        return cors_headers()
    
    # RDS Configuration
    RDS_CONFIG = {
        'host': 'notebook-db.cscpnqmixnxc.us-east-1.rds.amazonaws.com',
        'database': 'notebookdb',
        'user': 'notebookadmin',
        'password': '12345678',
        'port': 5432
    }
    
    # Check if this is an API request
    is_api_request = check_api_request(headers, http_method, query_params)
    
    if is_api_request:
        return handle_api_request(event, http_method, query_params, RDS_CONFIG)
    
    # Serve HTML page
    return serve_html_page()

def cors_headers():
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': ''
    }

def check_api_request(headers, http_method, query_params):
    accept_header = headers.get('Accept') or headers.get('accept', '')
    content_type = headers.get('Content-Type') or headers.get('content-type', '')
    
    return (
        'application/json' in accept_header or
        'application/json' in content_type or
        http_method in ['POST', 'DELETE'] or
        bool(query_params)
    )

def handle_api_request(event, http_method, query_params, rds_config):
    if not PG8000_AVAILABLE:
        return handle_setup_mode(event, http_method, query_params, rds_config)
    
    try:
        # Connect to RDS PostgreSQL using pg8000
        return handle_database_operations(event, http_method, query_params, rds_config)
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return handle_database_error(event, http_method, query_params, rds_config, str(e))

def handle_database_operations(event, http_method, query_params, rds_config):
    """Handle actual database operations with pg8000"""
    conn = None
    try:
        # Connect to PostgreSQL
        conn = pg8000.connect(
            host=rds_config['host'],
            database=rds_config['database'],
            user=rds_config['user'],
            password=rds_config['password'],
            port=rds_config['port']
        )
        
        # Create table if it doesn't exist
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        
        if http_method == 'GET':
            return handle_get_notes(conn)
        elif http_method == 'POST':
            return handle_add_note(event, conn)
        elif http_method == 'DELETE':
            return handle_delete_note(query_params, conn)
        else:
            return method_not_allowed()
            
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def handle_get_notes(conn):
    """Get all notes from database"""
    with conn.cursor() as cur:
        cur.execute("SELECT id, content, created_at FROM notes ORDER BY created_at DESC")
        notes = []
        for row in cur.fetchall():
            notes.append({
                'id': row[0],
                'content': row[1],
                'created_at': row[2].isoformat() if row[2] else None
            })
    
    return success_response(notes)

def handle_add_note(event, conn):
    """Add a new note to database"""
    body = get_request_body(event)
    content = body.get('content', '').strip()
    
    if not content:
        return error_response('Content cannot be empty', 400)
    
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO notes (content) VALUES (%s) RETURNING id, content, created_at",
            (content,)
        )
        result = cur.fetchone()
        new_note = {
            'id': result[0],
            'content': result[1],
            'created_at': result[2].isoformat() if result[2] else None
        }
        conn.commit()
    
    return {
        'statusCode': 201,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'message': 'Note saved to RDS PostgreSQL database',
            'note': new_note
        })
    }

def handle_delete_note(query_params, conn):
    """Delete a note from database"""
    note_id = query_params.get('id')
    if note_id and note_id.isdigit():
        note_id = int(note_id)
        with conn.cursor() as cur:
            cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
            deleted_count = cur.rowcount
            conn.commit()
        
        if deleted_count > 0:
            return success_response({
                'success': True,
                'message': f'Note {note_id} deleted from database'
            })
        else:
            return error_response(f'Note {note_id} not found', 404)
    else:
        return error_response('Valid note ID required', 400)

def handle_setup_mode(event, http_method, query_params, rds_config):
    """Handle requests when pg8000 is not available"""
    if http_method == 'GET':
        return success_response({
            'notes': [],
            'status': 'setup_required',
            'message': 'pg8000 library not available',
            'database_info': rds_config,
            'setup_instructions': 'Add pg8000 layer to enable database connectivity'
        })
    elif http_method == 'POST':
        return error_response('Database not available. Add pg8000 layer to enable saving notes.', 503)
    elif http_method == 'DELETE':
        return error_response('Database not available. Add pg8000 layer to enable deleting notes.', 503)
    else:
        return method_not_allowed()

def handle_database_error(event, http_method, query_params, rds_config, error_msg):
    """Handle database connection errors"""
    if http_method == 'GET':
        return success_response({
            'notes': [],
            'status': 'connection_error',
            'message': f'Database connection failed: {error_msg}',
            'database_info': rds_config,
            'troubleshooting': 'Check RDS security groups and network connectivity'
        })
    else:
        return error_response(f'Database error: {error_msg}', 503)

def get_request_body(event):
    body = event.get('body', '{}')
    if isinstance(body, str):
        return json.loads(body)
    return body

def success_response(data):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(data)
    }

def error_response(message, status_code=400):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': message})
    }

def method_not_allowed():
    return error_response('Method not allowed', 405)

def serve_html_page():
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        },
        'body': HTML_PAGE
    }

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AWS RDS Notebook</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2196f3, #1976d2);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .status-panel {
            background: #e8f5e8;
            padding: 20px;
            border-left: 5px solid #4caf50;
            margin: 20px;
            border-radius: 8px;
        }
        .warning-panel {
            background: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 20px;
            margin: 20px;
            border-radius: 8px;
            color: #856404;
        }
        .error-panel {
            background: #f8d7da;
            border-left: 5px solid #dc3545;
            padding: 20px;
            margin: 20px;
            border-radius: 8px;
            color: #721c24;
        }
        .setup-panel {
            background: #d1ecf1;
            border-left: 5px solid #17a2b8;
            padding: 20px;
            margin: 20px;
            border-radius: 8px;
            color: #0c5460;
        }
        .input-section {
            padding: 0 20px 20px;
        }
        textarea {
            width: 100%;
            height: 120px;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            transition: border-color 0.3s;
        }
        textarea:focus {
            outline: none;
            border-color: #2196f3;
            box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
        }
        .buttons {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        button {
            flex: 1;
            padding: 15px 25px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #2196f3;
            color: white;
        }
        .btn-primary:hover:not(:disabled) {
            background: #1976d2;
            transform: translateY(-2px);
        }
        .btn-primary:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background: #545b62;
            transform: translateY(-2px);
        }
        .notes-section {
            padding: 20px;
        }
        .note {
            background: #f8f9fa;
            border-left: 4px solid #2196f3;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .note-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .note-date {
            color: #6c757d;
            font-size: 0.9em;
        }
        .note-content {
            line-height: 1.6;
            margin-bottom: 10px;
        }
        .delete-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
        }
        .delete-btn:hover {
            background: #c82333;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        .code-block {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 14px;
            margin: 10px 0;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📓 AWS RDS Notebook</h1>
            <p>Python 3.13 • PostgreSQL RDS</p>
        </div>
        
        <div id="statusPanel" class="status-panel">
            <strong>🔍 Checking database connectivity...</strong>
        </div>
        
        <div id="setupPanel" class="setup-panel" style="display: none;">
            <strong>🚀 Setup Required</strong>
            <p>To connect to RDS PostgreSQL, add pg8000 as a Lambda layer:</p>
            <div class="code-block">
# Create layer locally:<br>
mkdir python<br>
pip install pg8000 -t python/<br>
zip -r pg8000-layer.zip python/
            </div>
            <p>Then upload as a custom Lambda layer and attach to this function.</p>
        </div>
        
        <div class="input-section">
            <textarea 
                id="noteContent" 
                placeholder="💡 Type your note here..."
            ></textarea>
            <div class="buttons">
                <button class="btn-primary" onclick="addNote()" id="addBtn">
                    💾 Save Note
                </button>
                <button class="btn-secondary" onclick="loadNotes()">
                    🔄 Refresh
                </button>
            </div>
        </div>
        
        <div class="notes-section">
            <h3>Your Notes</h3>
            <div id="notesList">
                <div class="loading">Checking database status...</div>
            </div>
        </div>
    </div>

    <script>
        let dbConnected = false;
        
        async function loadNotes() {
            try {
                showLoading();
                const response = await fetch(window.location.href, {
                    headers: { 
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    }
                });
                
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                
                const data = await response.json();
                updateStatusPanel(data);
                
                if (data.notes !== undefined) {
                    displayNotes(data.notes);
                } else {
                    displayNotes(data);
                }
                
            } catch (error) {
                showError('Failed to load notes: ' + error.message);
            }
        }
        
        function updateStatusPanel(data) {
            const statusPanel = document.getElementById('statusPanel');
            const setupPanel = document.getElementById('setupPanel');
            
            if (data.status === 'setup_required') {
                statusPanel.innerHTML = `
                    <strong>❌ Database Connection Not Available</strong>
                    <p>pg8000 library required to connect to RDS PostgreSQL</p>
                `;
                statusPanel.className = 'warning-panel';
                setupPanel.style.display = 'block';
                document.getElementById('addBtn').disabled = true;
                dbConnected = false;
            } else if (data.status === 'connection_error') {
                statusPanel.innerHTML = `
                    <strong>❌ Database Connection Failed</strong>
                    <p>${data.message}</p>
                    <p><strong>Troubleshooting:</strong> ${data.troubleshooting}</p>
                `;
                statusPanel.className = 'error-panel';
                document.getElementById('addBtn').disabled = true;
                dbConnected = false;
            } else {
                statusPanel.innerHTML = `
                    <strong>✅ Connected to RDS PostgreSQL</strong>
                    <p>Database: notebookdb | Using pg8000 driver</p>
                `;
                statusPanel.className = 'status-panel';
                setupPanel.style.display = 'none';
                document.getElementById('addBtn').disabled = false;
                dbConnected = true;
            }
        }
        
        function displayNotes(notes) {
            const container = document.getElementById('notesList');
            
            if (!notes || notes.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <h3>No notes yet</h3>
                        <p>Add your first note above!</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = notes.map(note => `
                <div class="note">
                    <div class="note-header">
                        <div class="note-date">
                            📅 ${new Date(note.created_at).toLocaleString()}
                        </div>
                        <button class="delete-btn" onclick="deleteNote(${note.id})" ${!dbConnected ? 'disabled style="background: #6c757d;"' : ''}>
                            🗑️ Delete
                        </button>
                    </div>
                    <div class="note-content">${escapeHtml(note.content)}</div>
                </div>
            `).join('');
        }
        
        async function addNote() {
            if (!dbConnected) {
                alert('Database not connected. Please setup pg8000 layer first.');
                return;
            }
            
            const content = document.getElementById('noteContent').value.trim();
            if (!content) {
                alert('Please enter some content for your note');
                return;
            }
            
            const btn = document.getElementById('addBtn');
            const originalText = btn.innerHTML;
            
            try {
                btn.disabled = true;
                btn.innerHTML = '⏳ Saving to RDS...';
                
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ content })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    document.getElementById('noteContent').value = '';
                    alert('✅ ' + (result.message || 'Note saved successfully'));
                    await loadNotes();
                } else {
                    throw new Error(result.error || 'Failed to add note');
                }
                
            } catch (error) {
                alert('❌ Error: ' + error.message);
            } finally {
                btn.disabled = !dbConnected;
                btn.innerHTML = originalText;
            }
        }
        
        async function deleteNote(noteId) {
            if (!dbConnected) {
                alert('Database not connected. Please setup pg8000 layer first.');
                return;
            }
            
            if (!confirm('Are you sure you want to delete this note from the database?')) return;
            
            try {
                const response = await fetch(window.location.href + '?id=' + noteId, {
                    method: 'DELETE',
                    headers: { 'Accept': 'application/json' }
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert('✅ ' + (result.message || 'Note deleted successfully'));
                    await loadNotes();
                } else {
                    throw new Error(result.error || 'Failed to delete note');
                }
            } catch (error) {
                alert('❌ Error: ' + error.message);
            }
        }
        
        function showLoading() {
            document.getElementById('notesList').innerHTML = '<div class="loading">Loading notes...</div>';
        }
        
        function showError(message) {
            document.getElementById('notesList').innerHTML = `
                <div style="text-align: center; padding: 20px; color: #dc3545;">
                    ${message}
                </div>
            `;
        }
        
        function escapeHtml(unsafe) {
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }
        
        // Load notes when page loads
        document.addEventListener('DOMContentLoaded', loadNotes);
    </script>
</body>
</html>
"""