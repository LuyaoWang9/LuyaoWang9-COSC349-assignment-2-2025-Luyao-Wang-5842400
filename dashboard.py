import os
import mysql.connector
from flask import Flask, render_template, jsonify

DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_USER = os.environ.get("DB_USER", "expense_user")
DB_PASS = os.environ.get("DB_PASS", "password")
DB_NAME = os.environ.get("DB_NAME", "expenses")

def get_conn():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
    )

app = Flask(__name__)

@app.route("/")
def dashboard():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name, SUM(amount) as total FROM bills GROUP BY name ORDER BY total DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("dashboard.html", rows=rows)

@app.route("/summary")
def summary():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name, SUM(amount) as total FROM bills GROUP BY name ORDER BY total DESC")
    data = [{"name": n, "total": float(t)} for (n, t) in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"summary": data})

@app.route("/health")
def health():
    try:
        conn = get_conn()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=True)