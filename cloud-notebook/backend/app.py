from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from datetime import datetime
import time

app = Flask(__name__)
CORS(app)

# MySQL RDS configuration - UPDATE PASSWORD!
DB_CONFIG = {
    'host': 'cloud-notebook-mysql.cscpnqmixnxc.us-east-1.rds.amazonaws.com',
    'database': 'notebook',
    'user': 'admin',
    'password': 'wanlu083',  
    'port': 3306
}

def get_db_connection():
    """Create and return a connection to MySQL RDS"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to RDS: {e}")
        raise

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ MySQL RDS database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

@app.route('/')
def home():
    return jsonify({
        'message': 'Cloud Notebook API is running with Amazon RDS MySQL!',
        'status': 'healthy',
        'database': 'Amazon RDS MySQL',
        'rds_endpoint': DB_CONFIG['host'],
        'port': 5054
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'Amazon RDS MySQL',
            'rds_endpoint': DB_CONFIG['host'],
            'timestamp': datetime.now().isoformat(),
            'test_result': result[0] if result else None
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'Amazon RDS MySQL',
            'error': str(e)
        }), 500

@app.route('/notes', methods=['GET'])
def get_notes():
    """Get all notes, sorted by most recently updated"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT id, title, content, created_at, updated_at 
            FROM notes 
            ORDER BY updated_at DESC
        ''')
        notes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for note in notes:
            if note['created_at']:
                note['created_at'] = note['created_at'].isoformat()
            if note['updated_at']:
                note['updated_at'] = note['updated_at'].isoformat()
        
        return jsonify(notes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notes', methods=['POST'])
def create_note():
    """Create a new note"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        title = data.get('title', 'Untitled Note')
        content = data.get('content', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO notes (title, content) VALUES (%s, %s)',
            (title, content)
        )
        note_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'id': note_id, 
            'message': 'Note created successfully in Amazon RDS MySQL',
            'title': title,
            'content': content,
            'database': 'Amazon RDS MySQL'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, title, content, created_at, updated_at FROM notes WHERE id = %s', (note_id,))
        note = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if note is None:
            return jsonify({'error': 'Note not found'}), 404
        
        if note['created_at']:
            note['created_at'] = note['created_at'].isoformat()
        if note['updated_at']:
            note['updated_at'] = note['updated_at'].isoformat()
            
        return jsonify(note)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update an existing note"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        title = data.get('title', 'Untitled Note')
        content = data.get('content', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM notes WHERE id = %s', (note_id,))
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Note not found'}), 404
        
        cursor.execute(
            'UPDATE notes SET title = %s, content = %s WHERE id = %s',
            (title, content, note_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Note updated successfully',
            'id': note_id,
            'title': title,
            'content': content
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM notes WHERE id = %s', (note_id,))
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Note not found'}), 404
        
        cursor.execute('DELETE FROM notes WHERE id = %s', (note_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Note deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about notes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM notes')
        total_notes = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM notes WHERE updated_at >= NOW() - INTERVAL 1 DAY')
        recent_notes = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_notes': total_notes,
            'recent_notes_24h': recent_notes,
            'database': 'Amazon RDS MySQL',
            'rds_endpoint': DB_CONFIG['host']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Cloud Notebook Backend on Port 8080...")
    print(f"🌐 RDS Endpoint: {DB_CONFIG['host']}")
    print("🔄 Initializing database...")
    init_db()
    print("✅ Production Backend ready! Available at: http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)
