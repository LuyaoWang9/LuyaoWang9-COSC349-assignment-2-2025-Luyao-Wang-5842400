from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from datetime import datetime
import time
import boto3
import json
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# MySQL RDS configuration
DB_CONFIG = {
    'host': 'cloud-notebook-mysql.cscpnqmixnxc.us-east-1.rds.amazonaws.com',
    'database': 'notebook',
    'user': 'admin',
    'password': 'wanlu083',  
    'port': 3306
}

# S3 Configuration
S3_CONFIG = {
    'bucket_name': 'cloud-notebook-attachments',
    'region': 'us-east-1'
}

def get_db_connection():
    """Create and return a connection to MySQL RDS"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to RDS: {e}")
        raise

def get_s3_client():
    """Create and return S3 client"""
    return boto3.client('s3', region_name=S3_CONFIG['region'])

def get_lambda_client():
    """Create and return Lambda client"""
    return boto3.client('lambda', region_name='us-east-1')

def init_s3_bucket():
    """Initialize S3 bucket if it doesn't exist"""
    try:
        s3 = get_s3_client()
        
        # Check if bucket exists, create if not
        try:
            s3.head_bucket(Bucket=S3_CONFIG['bucket_name'])
            print(f"✅ S3 bucket {S3_CONFIG['bucket_name']} already exists")
        except:
            if S3_CONFIG['region'] == 'us-east-1':
                s3.create_bucket(Bucket=S3_CONFIG['bucket_name'])
            else:
                s3.create_bucket(
                    Bucket=S3_CONFIG['bucket_name'],
                    CreateBucketConfiguration={'LocationConstraint': S3_CONFIG['region']}
                )
            print(f"✅ Created S3 bucket: {S3_CONFIG['bucket_name']}")
            
        return True
    except Exception as e:
        print(f"❌ S3 initialization error: {e}")
        return False

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
        
        # Initialize S3 bucket
        init_s3_bucket()
        
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

@app.route('/')
def home():
    return jsonify({
        'message': 'Cloud Notebook API is running with Amazon RDS MySQL and S3!',
        'status': 'healthy',
        'database': 'Amazon RDS MySQL',
        'file_storage': 'Amazon S3',
        'rds_endpoint': DB_CONFIG['host'],
        's3_bucket': S3_CONFIG['bucket_name'],
        'port': 8080
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
            'file_storage': 'Amazon S3',
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

@app.route('/lambda-stats', methods=['GET'])
def get_lambda_stats():
    """Get statistics from AWS Lambda function"""
    try:
        print("🔄 Attempting to invoke Lambda function...")
        
        # Initialize Lambda client
        lambda_client = get_lambda_client()
        
        # Invoke Lambda function
        response = lambda_client.invoke(
            FunctionName='cloud-notebook-stats',
            InvocationType='RequestResponse'
        )
        
        # Parse Lambda response
        lambda_response = json.loads(response['Payload'].read())
        
        return jsonify({
            'message': 'Statistics from AWS Lambda',
            'lambda_response': lambda_response,
            'services_used': ['AWS Lambda', 'RDS MySQL', 'S3']
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to get Lambda statistics'
        }), 500

@app.route('/notes/<int:note_id>/attachments', methods=['GET'])
def get_note_attachments(note_id):
    """Get all attachments for a note"""
    try:
        s3 = get_s3_client()
        
        # List objects with note_id prefix
        response = s3.list_objects_v2(
            Bucket=S3_CONFIG['bucket_name'],
            Prefix=f"attachments/{note_id}/"
        )
        
        attachments = []
        if 'Contents' in response:
            for obj in response['Contents']:
                attachments.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'filename': obj['Key'].split('/')[-1]
                })
        
        return jsonify({
            'note_id': note_id,
            'attachments': attachments
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<int:note_id>/attachments', methods=['POST'])
def upload_attachment(note_id):
    """Upload a file attachment to S3"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        s3_key = f"attachments/{note_id}/{unique_filename}"
        
        # Upload to S3
        s3 = get_s3_client()
        s3.upload_fileobj(
            file,
            S3_CONFIG['bucket_name'],
            s3_key,
            ExtraArgs={
                'Metadata': {
                    'original-filename': original_filename,
                    'note-id': str(note_id),
                    'uploaded-at': datetime.now().isoformat()
                }
            }
        )
        
        # Generate presigned URL for access
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_CONFIG['bucket_name'], 'Key': s3_key},
            ExpiresIn=3600
        )
        
        return jsonify({
            'message': 'File uploaded successfully',
            's3_key': s3_key,
            'filename': original_filename,
            'presigned_url': presigned_url,
            'note_id': note_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/attachments/<path:s3_key>', methods=['GET'])
def get_attachment(s3_key):
    """Get a presigned URL for downloading an attachment"""
    try:
        s3 = get_s3_client()
        
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_CONFIG['bucket_name'], 'Key': s3_key},
            ExpiresIn=3600
        )
        
        return jsonify({
            'download_url': presigned_url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/attachments/<path:s3_key>', methods=['DELETE'])
def delete_attachment(s3_key):
    """Delete an attachment from S3"""
    try:
        s3 = get_s3_client()
        
        s3.delete_object(
            Bucket=S3_CONFIG['bucket_name'],
            Key=s3_key
        )
        
        return jsonify({'message': 'Attachment deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<int:note_id>/backup', methods=['POST'])
def backup_note_to_s3(note_id):
    """Create a backup of a note to S3"""
    try:
        # Get note from database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM notes WHERE id = %s', (note_id,))
        note = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        # Create backup in S3
        s3 = get_s3_client()
        backup_key = f"backups/notes/{note_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        backup_data = {
            'note': note,
            'backup_timestamp': datetime.now().isoformat(),
            'backup_type': 'manual'
        }
        
        s3.put_object(
            Bucket=S3_CONFIG['bucket_name'],
            Key=backup_key,
            Body=json.dumps(backup_data, indent=2),
            ContentType='application/json'
        )
        
        return jsonify({
            'message': 'Note backed up successfully',
            'backup_key': backup_key,
            'note_id': note_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Cloud Notebook Backend on Port 8080...")
    print(f"🌐 RDS Endpoint: {DB_CONFIG['host']}")
    print("🔄 Initializing database and S3...")
    init_db()
    print("✅ Production Backend ready! Available at: http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)
