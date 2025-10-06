AWS RDS Notebook

A cloud-native note-taking application built with AWS Lambda serverless technologies and PostgreSQL database.

🚀 Live Application

Application URL: https://rqhl0dys2e.execute-api.us-east-1.amazonaws.com/prod/notebook

📋 Features

✨ Create, view, and delete notes
💾 Persistent storage in Amazon RDS PostgreSQL
📱 Responsive web interface
🚀 Serverless architecture
🔒 Secure database connections
⚡ Fast and scalable

🏗️ Architecture
Web Browser → API Gateway → AWS Lambda → RDS PostgreSQL

Installation
1. Clone the repository
git clone https://github.com/LuyaoWang9/LuyaoWang9-COSC349-assignment-2-2025-Luyao-Wang-5842400.git
cd aws-rds-notebook
2. Set up environment variables
export RDS_HOST=notebook-db.cscpnqmixnxc.us-east-1.rds.amazonaws.com
export RDS_DATABASE=notebookdb
export RDS_USER=notebookadmin
export RDS_PASSWORD=12345678
export RDS_PORT=5432
3. Install dependencies
pip install pg8000

📦 Deployment

Manual Deployment to AWS

1. Create RDS PostgreSQL Instance

Go to AWS RDS Console
Create PostgreSQL instance
Note the endpoint, database name, username, and password
Configure security groups to allow Lambda access
Deploy Lambda Function

2. Deploy Lambda Function

Create new Lambda function (Python 3.13)
Upload the lambda_function.py code
Add pg8000 layer (see Layer Setup below)
Configure environment variables:
RDS_HOST=notebook-db.cscpnqmixnxc.us-east-1.rds.amazonaws.com
RDS_DATABASE=notebookdb
RDS_USER=notebookadmin
RDS_PASSWORD=12345678
RDS_PORT=5432
Set up API Gateway

3. Set up API Gateway

Create new REST API
Create resource and methods (GET, POST, DELETE, OPTIONS)
Enable CORS
Deploy API

4. Configure IAM Role

Ensure Lambda execution role has:
rds-db:connect permission
Basic Lambda execution role

Layer Setup

The application requires pg8000 PostgreSQL driver. Create a layer:

# Create layer package
mkdir python
pip install pg8000 -t python/
zip -r pg8000-layer.zip python/
# Upload to AWS Lambda as a layer


🗄️ Database Schema

CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


💻 Usage

Access the application through the provided URL
Type your note in the text area
Click "Save to Database" to persist the note
View all notes in the list below
Delete notes using the delete button

💰 Cost Estimation

Idle: ~$14.71/month (primarily RDS instance)
Light Usage: ~$14.93/month (minimal Lambda costs)
See project report for detailed cost breakdown.

Developed for COSC349 Cloud Computing Assignment 2
University of Otago, 2025
Luyao Wang
5842400