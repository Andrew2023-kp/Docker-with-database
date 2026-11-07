import os
import time
from flask import Flask, request, redirect, render_template_string
import mysql.connector

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "mysql-db"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.environ["DB_PASSWORD"],
        database=os.getenv("DB_NAME", "appdb")
    )

def query_db(sql, params=(), fetch=False):
    conn = get_db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        result = cursor.fetchall() if fetch else None
        conn.commit()
        cursor.close()
        return result
    finally:
        conn.close()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MySQL Web App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; max-width: 850px; margin: 40px auto;
               padding: 0 16px; background: #f4f7fb; color: #172033; }
        .card { background: white; padding: 24px; border-radius: 12px;
                margin-bottom: 20px; box-shadow: 0 3px 12px #0001; }
        input, button { padding: 11px; margin: 5px 0; }
        input { box-sizing: border-box; width: 100%; border: 1px solid #ccc;
                border-radius: 6px; }
        button { background: #1769e0; color: white; border: 0;
                 border-radius: 6px; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 10px; border-bottom: 1px solid #eee; }
        .delete { background: #d93636; }
    </style>
</head>
<body>
    <h1>MySQL Data Manager</h1>
    <p>Add and manage records stored in your MySQL database.</p>
    <div class="card">
        <h2>Add a person</h2>
        <form action="/add" method="post">
            <input name="name" placeholder="Full name" maxlength="100" required>
            <input name="email" type="email" placeholder="Email address"
                   maxlength="254" required>
            <button type="submit">Save record</button>
        </form>
    </div>
    <div class="card">
        <h2>Saved records ({{ records|length }})</h2>
        <table>
            <tr><th>ID</th><th>Name</th><th>Email</th><th>Action</th></tr>
            {% for r in records %}
            <tr>
                <td>{{ r.id }}</td>
                <td>{{ r.name }}</td>
                <td>{{ r.email }}</td>
                <td>
                    <form action="/delete/{{ r.id }}" method="post">
                        <button class="delete" type="submit">Delete</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.get("/")
def index():
    records = query_db(
        "SELECT id, name, email FROM people ORDER BY id DESC",
        fetch=True
    )
    return render_template_string(HTML, records=records)

@app.post("/add")
def add():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()

    if not name or len(name) > 100 or not email or len(email) > 254:
        return "Invalid name or email", 400

    query_db(
        "INSERT INTO people (name, email) VALUES (%s, %s)",
        (name, email)
    )
    return redirect("/")

@app.post("/delete/<int:record_id>")
def delete(record_id):
    query_db("DELETE FROM people WHERE id = %s", (record_id,))
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
