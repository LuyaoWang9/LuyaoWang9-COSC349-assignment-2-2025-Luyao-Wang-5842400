from flask import Flask, request, jsonify, render_template
import pymysql
from flask_cors import CORS
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
db_config = {
    'host': 'data.cscpnqmixnxc.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': '12345678',
    'database': 'assignment',
    'port': 3306,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def init_db():
    """Initialize database connection and create tables"""
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed BOOLEAN DEFAULT FALSE
                )
            ''')
            logger.info("✅ Database tables created successfully")
        connection.commit()
        connection.close()
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")

def log_notification(task_id, task_title, action):
    """Log notifications to console (simulating AWS services)"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if action == 'completed':
            message = f"🔔 NOTIFICATION: Task Completed - '{task_title}' (ID: {task_id}) at {timestamp}"
        elif action == 'created':
            message = f"🔔 NOTIFICATION: New Task Created - '{task_title}' (ID: {task_id}) at {timestamp}"
        else:
            message = f"🔔 NOTIFICATION: Task {action} - '{task_title}' (ID: {task_id}) at {timestamp}"
        
        logger.info(message)
        return True
        
    except Exception as e:
        logger.error(f"❌ Notification logging failed: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            tasks = cursor.fetchall()
        connection.close()
        return jsonify(tasks)
    except Exception as e:
        logger.error(f"❌ Error getting tasks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Add a new task"""
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
            
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (title, description) VALUES (%s, %s)",
                (data['title'], data.get('description', ''))
            )
            task_id = cursor.lastrowid
        connection.commit()
        connection.close()
        
        # Log notification
        notification_sent = log_notification(task_id, data['title'], 'created')
        
        return jsonify({
            'message': 'Task added successfully',
            'notification_sent': notification_sent,
            'task_id': task_id
        })
    except Exception as e:
        logger.error(f"❌ Error adding task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    """Mark task as completed"""
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # First, check if the task exists and get its title
            cursor.execute("SELECT title FROM tasks WHERE id = %s", (task_id,))
            task = cursor.fetchone()
            
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            
            # Update task completion
            cursor.execute(
                "UPDATE tasks SET completed = TRUE WHERE id = %s",
                (task_id,)
            )
                    
        connection.commit()
        connection.close()
        
        # Log notification
        notification_sent = log_notification(task_id, task['title'], 'completed')
        
        return jsonify({
            'message': 'Task completed successfully',
            'notification_sent': notification_sent
        })
    except Exception as e:
        logger.error(f"❌ Error completing task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Task deleted successfully'})
    except Exception as e:
        logger.error(f"❌ Error deleting task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        connection = pymysql.connect(**db_config)
        connection.close()
        
        return jsonify({
            'status': 'healthy', 
            'database': 'connected',
            'port': 5020,
            'services': {
                'aws_rds': 'connected',
                'notifications': 'logging_to_console',
                'ec2_backend': 'running',
                'ec2_frontend': 'external'
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy', 
            'error': str(e)
        }), 500

@app.route('/api/test-notification', methods=['POST'])
def test_notification():
    """Test endpoint for notification system"""
    try:
        data = request.get_json()
        task_id = data.get('task_id', 999)
        task_title = data.get('task_title', 'Test Task')
        action = data.get('action', 'test')
        
        success = log_notification(task_id, task_title, action)
        
        return jsonify({
            'message': 'Notification test executed',
            'notification_sent': success,
            'note': 'Check backend console for notification logs'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Initializing Task Manager Backend...")
    print(f"📊 Database: {db_config['host']}")
    print(f"🔌 Server running on port: 5020")
    print("💡 Using AWS RDS as non-EC2 service")
    print("🔔 Notifications are logged to console")
    print("=" * 50)
    init_db()
    app.run(host='0.0.0.0', port=5020, debug=True)