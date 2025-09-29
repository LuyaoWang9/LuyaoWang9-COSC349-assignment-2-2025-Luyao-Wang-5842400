import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash

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
app.secret_key = "cloud-secret-key"

@app.route("/", methods=["GET"])
def index():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, amount, description, created_at FROM bills ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("index.html", rows=rows)
    except Exception as e:
        return f"Database connection error: {str(e)}", 500

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    amount = request.form.get("amount", "").strip()
    description = request.form.get("description", "").strip()
    
    if not name or not amount or not description:
        flash("All fields are required")
        return redirect(url_for("index"))
    
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO bills (name, amount, description) VALUES (%s, %s, %s)",
                    (name, float(amount), description))
        conn.commit()
        cur.close()
        conn.close()
        flash("Bill added successfully!")
    except Exception as e:
        flash(f"Error adding bill: {str(e)}")
    
    return redirect(url_for("index"))

@app.route("/health")
def health():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "healthy", "service": "frontend", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500

@app.post("/delete/<int:bill_id>")
def delete_bill(bill_id: int):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM bills WHERE id = %s", (bill_id,))
        conn.commit()
        deleted = cur.rowcount
        cur.close()
        conn.close()
        
        if deleted:
            flash(f"Deleted bill #{bill_id}")
        else:
            flash(f"No bill found with id #{bill_id}")
    except Exception as e:
        flash(f"Error deleting bill: {str(e)}")
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5051, debug=True)
