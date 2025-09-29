import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import abort

DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_USER = os.environ.get("DB_USER", "expense_user")
DB_PASS = os.environ.get("DB_PASS", "password")
DB_NAME = os.environ.get("DB_NAME", "expenses")

def get_conn():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
    )

app = Flask(__name__)
app.secret_key = "dev-secret"

@app.route("/", methods=["GET"])
def index():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, amount, description FROM bills ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", rows=rows)

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    amount = request.form.get("amount", "").strip()
    description = request.form.get("description", "").strip()
    if not name or not amount or not description:
        flash("All fields are required")
        return redirect(url_for("index"))
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO bills (name, amount, description) VALUES (%s, %s, %s)",
                (name, amount, description))
    conn.commit()
    cur.close()
    conn.close()
    flash("Bill added")
    return redirect(url_for("index"))

@app.route("/health")
def health():
    try:
        conn = get_conn()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}, 500
    
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
        return redirect(url_for("index"))
    except Exception as e:
        # Optional: log e
        flash("Failed to delete bill")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
