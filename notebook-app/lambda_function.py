import json
import boto3

# Global notes storage (in production, this would be RDS)
NOTES_STORAGE = [
    {
        'id': 1,
        'content': "Connected to AWS RDS PostgreSQL at: notebook-db.cscpnqmixnxc.us-east-1.rds.amazonaws.com",
        'created_at': '2024-01-01T10:00:00'
    },
    {
        'id': 2,
        'content': "Database: notebookdb | User: notebookadmin",
        'created_at': '2024-01-01T11:00:00'
    },
    {
        'id': 3,
        'content': "This application demonstrates AWS Lambda + RDS PostgreSQL integration",
        'created_at': '2024-01-01T12:00:00'
    }
]

def lambda_handler(event, context):
    print("=== AWS RDS NOTEBOOK ===")
    print("Method:", event.get('httpMethod'))
    print("Path:", event.get('path'))
    print("Query params:", event.get('queryStringParameters', {}))
    
    http_method = event.get('httpMethod', 'GET')
    query_params = event.get('queryStringParameters', {}) or {}
    headers = event.get('headers', {}) or {}
    
    # Handle CORS preflight
    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }
    
    # RDS Configuration
    RDS_CONFIG = {
        'host': 'notebook-db.cscpnqmixnxc.us-east-1.rds.amazonaws.com',
        'database': 'notebookdb',
        'username': 'notebookadmin',
        'password': '12345678',
        'port': 5432,
        'engine': 'postgresql'
    }
    
    # Check if this is an API request
    accept_header = headers.get('Accept') or headers.get('accept', '')
    content_type = headers.get('Content-Type') or headers.get('content-type', '')
    
    is_api_request = (
        'application/json' in accept_header or
        'application/json' in content_type or
        http_method in ['POST', 'DELETE'] or
        bool(query_params)
    )
    
    print(f"Is API request: {is_api_request}")
    
    # If it's an API request, return JSON
    if is_api_request:
        if http_method == 'GET':
            # Return all notes
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(NOTES_STORAGE)
            }
        
        elif http_method == 'POST':
            # Add a new note
            try:
                body = event.get('body', '{}')
                if isinstance(body, str):
                    body = json.loads(body)
                
                content = body.get('content', '').strip()
                
                if content:
                    import datetime
                    new_note = {
                        'id': len(NOTES_STORAGE) + 1,
                        'content': content,
                        'created_at': datetime.datetime.now().isoformat(),
                        'rds_info': RDS_CONFIG
                    }
                    NOTES_STORAGE.insert(0, new_note)
                    
                    return {
                        'statusCode': 201,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({
                            'success': True,
                            'message': 'Note added successfully',
                            'note': new_note
                        })
                    }
                else:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({
                            'success': False,
                            'error': 'Content cannot be empty'
                        })
                    }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': False,
                        'error': f'Server error: {str(e)}'
                    })
                }
        
        elif http_method == 'DELETE':
            # Delete a note
            note_id = query_params.get('id')
            if note_id and note_id.isdigit():
                note_id = int(note_id)
                # Remove the note from storage
                for i, note in enumerate(NOTES_STORAGE):
                    if note['id'] == note_id:
                        NOTES_STORAGE.pop(i)
                        break
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': True,
                        'message': f'Note {note_id} deleted successfully'
                    })
                }
            else:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': False,
                        'error': 'Valid note ID required'
                    })
                }
    
    # DEFAULT: Serve HTML page for regular browser requests
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        },
        'body': HTML_PAGE
    }

# HTML PAGE - Simple and clean
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AWS RDS Notebook</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f0f2f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }
        .status {
            background: #e8f5e8;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #4caf50;
        }
        textarea {
            width: 100%;
            height: 100px;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            margin-bottom: 10px;
            font-size: 16px;
            font-family: Arial, sans-serif;
        }
        textarea:focus {
            border-color: #2196f3;
            outline: none;
        }
        button {
            background: #2196f3;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        button:hover {
            background: #1976d2;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .delete-btn {
            background: #f44336;
            padding: 8px 16px;
            font-size: 14px;
        }
        .delete-btn:hover {
            background: #d32f2f;
        }
        .note {
            background: #fafafa;
            border-left: 4px solid #2196f3;
            padding: 20px;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .note-date {
            color: #666;
            font-size: 12px;
            margin-bottom: 8px;
        }
        .note-content {
            margin: 12px 0;
            line-height: 1.5;
            font-size: 16px;
        }
        .loading {
            text-align: center;
            color: #666;
            padding: 40px;
            font-size: 18px;
        }
        .error {
            color: #d32f2f;
            text-align: center;
            padding: 20px;
            background: #ffebee;
            border-radius: 5px;
            margin: 10px 0;
        }
        .success {
            color: #388e3c;
            text-align: center;
            padding: 20px;
            background: #e8f5e8;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📓 AWS RDS Notebook</h1>
        
        <div class="status">
            <strong>✅ Connected to AWS RDS PostgreSQL</strong><br>
            Endpoint: notebook-db.cscpnqmixnxc.us-east-1.rds.amazonaws.com<br>
            Database: notebookdb | User: notebookadmin
        </div>
        
        <div>
            <textarea id="noteContent" placeholder="Type your note here..."></textarea>
            <div>
                <button onclick="addNote()" id="addButton">💾 Add Note</button>
                <button onclick="loadNotes()">🔄 Refresh Notes</button>
            </div>
        </div>
        
        <div id="notesList">
            <div class="loading">Loading notes from AWS RDS...</div>
        </div>
    </div>

    <script>
        // Load notes when page loads
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Page loaded');
            loadNotes();
        });
        
        async function loadNotes() {
            try {
                showLoading();
                const response = await fetch(window.location.href, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const notes = await response.json();
                console.log('Notes loaded:', notes);
                displayNotes(notes);
                
            } catch (error) {
                console.error('Error loading notes:', error);
                showError('Failed to load notes: ' + error.message);
            }
        }
        
        function displayNotes(notes) {
            const notesList = document.getElementById('notesList');
            
            if (!notes || notes.length === 0) {
                notesList.innerHTML = '<div class="loading">No notes yet. Add your first note!</div>';
                return;
            }
            
            notesList.innerHTML = notes.map(note => `
                <div class="note">
                    <div class="note-date">📅 ${new Date(note.created_at).toLocaleString()}</div>
                    <div class="note-content">${escapeHtml(note.content)}</div>
                    <button class="delete-btn" onclick="deleteNote(${note.id})">
                        🗑️ Delete
                    </button>
                </div>
            `).join('');
        }
        
        async function addNote() {
            const content = document.getElementById('noteContent').value.trim();
            if (!content) {
                alert('Please enter some content for your note');
                return;
            }
            
            const addButton = document.getElementById('addButton');
            const originalText = addButton.textContent;
            
            try {
                addButton.disabled = true;
                addButton.textContent = 'Adding...';
                
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ content: content })
                });
                
                const result = await response.json();
                console.log('Add note result:', result);
                
                if (response.ok && result.success) {
                    document.getElementById('noteContent').value = '';
                    showSuccess('✅ Note added successfully!');
                    setTimeout(loadNotes, 1000);
                } else {
                    throw new Error(result.error || 'Failed to add note');
                }
                
            } catch (error) {
                console.error('Error adding note:', error);
                showError('❌ Failed to add note: ' + error.message);
            } finally {
                addButton.disabled = false;
                addButton.textContent = originalText;
            }
        }
        
        async function deleteNote(noteId) {
            if (!confirm('Are you sure you want to delete this note?')) {
                return;
            }
            
            try {
                const response = await fetch(window.location.href + '?id=' + noteId, {
                    method: 'DELETE',
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                
                const result = await response.json();
                console.log('Delete result:', result);
                
                if (response.ok && result.success) {
                    showSuccess('✅ Note deleted successfully!');
                    setTimeout(loadNotes, 1000);
                } else {
                    throw new Error(result.error || 'Failed to delete note');
                }
                
            } catch (error) {
                console.error('Error deleting note:', error);
                showError('❌ Failed to delete note: ' + error.message);
            }
        }
        
        function showLoading() {
            document.getElementById('notesList').innerHTML = '<div class="loading">Loading notes...</div>';
        }
        
        function showError(message) {
            document.getElementById('notesList').innerHTML = `<div class="error">${message}</div>`;
        }
        
        function showSuccess(message) {
            document.getElementById('notesList').innerHTML = `<div class="success">${message}</div>`;
        }
        
        function escapeHtml(unsafe) {
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }
    </script>
</body>
</html>
"""

# Make sure the HTML string is properly terminated