import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    """
    Lambda function to backup Cloud Notebook statistics to S3
    This counts as your additional non-EC2 cloud service
    """
    
    print("Starting Cloud Notebook backup...")
    
    try:
        # Initialize AWS clients
        s3_client = boto3.client('s3')
        
        # Create backup data
        backup_data = {
            'backup_timestamp': datetime.now().isoformat(),
            'service': 'Cloud Notebook Backup',
            'description': 'Daily statistics backup',
            'lambda_function': context.function_name,
            'request_id': context.aws_request_id,
            'note_count': 0,  # You could connect to RDS here
            'backup_type': 'automated'
        }
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"backups/notebook-backup-{timestamp}.json"
        
        # Upload to S3
        s3_client.put_object(
            Bucket='cloud-notebook-backups',
            Key=filename,
            Body=json.dumps(backup_data, indent=2),
            ContentType='application/json'
        )
        
        print(f"Backup completed: {filename}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Backup completed successfully',
                'backup_file': filename,
                'timestamp': backup_data['backup_timestamp']
            })
        }
        
    except Exception as e:
        print(f"Backup error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Backup failed'
            })
        }