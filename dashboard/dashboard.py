import os
import mysql.connector
from flask import Flask, render_template, jsonify

# RDS Configuration
DB_HOST = os.environ.get("DB_HOST", "shared-expense-db.cscpnqmixnxc.us-east-1.rds.amazonaws.com")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASS = os.environ.get("DB_PASS", "ExpenseApp2025!")
DB_NAME = os.environ.get("DB_NAME", "expenses")

def get_conn():
    return mysql.connector.connect(
        host=DB_HOST, 
        user=DB_USER, 
        password=DB_PASS, 
        database=DB_NAME,
        port=3306
    )

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/summary")
def summary():
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # Get total per person
        cur.execute("""
            SELECT name, SUM(amount) as total, COUNT(*) as bill_count 
            FROM bills 
            GROUP BY name 
            ORDER BY total DESC
        """)
        summary_data = []
        for (name, total, count) in cur.fetchall():
            summary_data.append({
                "name": name,
                "total": float(total),
                "bill_count": count
            })
        
        cur.close()
        conn.close()
        
        return jsonify({
            'summary': summary_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "healthy", "service": "dashboard", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=True)
