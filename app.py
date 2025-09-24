import os
import mysql.connector
import boto3
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from datetime import datetime

# Cloud configuration
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "expense_user")
DB_PASS = os.environ.get("DB_PASS", "password")
DB_NAME = os.environ.get("DB_NAME", "expenses")
API_SERVER_URL = os.environ.get("API_SERVER_URL", "http://localhost:8000")
S3_BUCKET = os.environ.get("S3_BUCKET", "expense-receipts")

def get_conn():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
    )

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Initialize S3 client
s3_client = boto3.client('s3')

@app.route("/", methods=["GET"])
def index():
    try:
        # Use API server instead of direct DB access
        response = requests.get(f"{API_SERVER_URL}/bills")
        if response.status_code == 200:
            bills = response.json()
        else:
            # Fallback to direct DB access
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT id, name, amount, description FROM bills ORDER BY id DESC")
            bills = [{"id": r[0], "name": r[1], "amount": r[2], "description": r[3]} for r in cur.fetchall()]
            cur.close()
            conn.close()
    except:
        bills = []
    
    return render_template("index.html", rows=bills)

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    amount = request.form.get("amount", "").strip()
    description = request.form.get("description", "").strip()
    
    if not name or not amount or not description:
        flash("All fields are required")
        return redirect(url_for("index"))
    
    try:
        # Send to API server
        response = requests.post(f"{API_SERVER_URL}/bills", json={
            "name": name,
            "amount": float(amount),
            "description": description
        })
        
        if response.status_code == 201:
            flash("Bill added successfully")
        else:
            # Fallback to direct DB
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("INSERT INTO bills (name, amount, description) VALUES (%s, %s, %s)",
                        (name, amount, description))
            conn.commit()
            cur.close()
            conn.close()
            flash("Bill added (fallback mode)")
            
    except Exception as e:
        flash(f"Error adding bill: {str(e)}")
    
    return redirect(url_for("index"))

@app.route("/upload-receipt", methods=["POST"])
def upload_receipt():
    if 'receipt' not in request.files:
        flash("No file selected")
        return redirect(url_for("index"))
    
    file = request.files['receipt']
    if file.filename == '':
        flash("No file selected")
        return redirect(url_for("index"))
    
    if file:
        # Upload to S3
        filename = f"receipts/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        s3_client.upload_fileobj(file, S3_BUCKET, filename)
        flash(f"Receipt uploaded: {filename}")
    
    return redirect(url_for("index"))

@app.route("/health")
def health():
    health_status = {"status": "ok", "services": {}}
    
    # Check database
    try:
        conn = get_conn()
        conn.close()
        health_status["services"]["database"] = "ok"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check API server
    try:
        response = requests.get(f"{API_SERVER_URL}/health", timeout=5)
        health_status["services"]["api"] = "ok" if response.status_code == 200 else "error"
    except:
        health_status["services"]["api"] = "error"
        health_status["status"] = "degraded"
    
    # Check S3
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET)
        health_status["services"]["s3"] = "ok"
    except:
        health_status["services"]["s3"] = "error"
        health_status["status"] = "degraded"
    
    return health_status

@app.post("/delete/<int:bill_id>")
def delete_bill(bill_id: int):
    try:
        response = requests.delete(f"{API_SERVER_URL}/bills/{bill_id}")
        if response.status_code == 200:
            flash(f"Deleted bill #{bill_id}")
        else:
            # Fallback
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM bills WHERE id = %s", (bill_id,))
            conn.commit()
            cur.close()
            conn.close()
            flash(f"Deleted bill #{bill_id} (fallback)")
    except Exception as e:
        flash(f"Failed to delete bill: {str(e)}")
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)