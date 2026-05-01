import os
import sqlite3
import hashlib
import traceback
import requests
from flask import Flask, request, render_template_string, render_template

app = Flask(__name__)

# [SECRET SCANNING DEMO]
# Dummy API Key to trigger GHAS Secret Scanning
DUMMY_OPENAI_API_KEY = "sk-abcdefghijklmnopqrstT3BlbkFJabcdefghijklmnopqrst"

# [A02: SECURITY MISCONFIGURATION DEMO]
# Vulnerability: CORS allow-all header applied globally
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

def mock_llm_call(prompt):
    """
    Simulates an LLM call.
    In a real scenario, this would send the prompt to an API.
    """
    return f"AI Response to: {prompt[:50]}..."

def init_db():
    """Initialize an in-memory SQLite DB with a users table for demos."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, password TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'admin', 'plaintext_password_123')")
    conn.commit()
    return conn

DB_CONN = init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    # [PROMPT INJECTION (LLM01) DEMO]
    # Vulnerability: Directly concatenating user input into the prompt.
    user_input = request.form.get("text", "")
    system_prompt = "Summarize the following text: "
    full_prompt = system_prompt + user_input  # TAINTED DATA

    response = mock_llm_call(full_prompt)
    return {"summary": response}

@app.route("/fetch", methods=["POST"])
def fetch_url():
    # [A01: BROKEN ACCESS CONTROL / SSRF DEMO]
    # Vulnerability: Fetching a user-provided URL without validation.
    target_url = request.form.get("url", "")
    try:
        # CodeQL should detect this as SSRF (py/full-ssrf)
        resp = requests.get(target_url, timeout=5)
        return {"content": resp.text[:200]}
    except Exception as e:
        # [A10: MISHANDLING OF EXCEPTIONAL CONDITIONS DEMO]
        # Vulnerability: Returning full stack trace to the client.
        return {"error": traceback.format_exc()}, 400

@app.route("/preview", methods=["POST"])
def preview():
    # [A05: INJECTION (XSS) DEMO]
    # Vulnerability: Returning unsanitized content to be rendered via innerHTML.
    content = request.form.get("content", "")
    # In index.html, this will be injected via JS innerHTML
    return {"html": content}

@app.route("/download", methods=["GET"])
def download():
    # [A01: BROKEN ACCESS CONTROL (Path Traversal) DEMO]
    # Vulnerability: User-controlled file path without sanitization.
    filename = request.args.get("file", "readme.txt")
    base_dir = "/app/static/files"
    # CodeQL should detect this as path injection (py/path-injection)
    filepath = os.path.join(base_dir, filename)
    try:
        with open(filepath, "r") as f:
            return {"content": f.read()}
    except Exception as e:
        return {"error": str(e)}, 404

@app.route("/user", methods=["GET"])
def get_user():
    # [A05: INJECTION (SQL Injection) DEMO]
    # Vulnerability: Directly interpolating user input into SQL query.
    name = request.args.get("name", "")
    # CodeQL should detect this as SQL injection (py/sql-injection)
    query = f"SELECT id, name FROM users WHERE name = '{name}'"
    try:
        cursor = DB_CONN.execute(query)
        rows = cursor.fetchall()
        return {"users": rows}
    except Exception as e:
        return {"error": traceback.format_exc()}, 500

@app.route("/register", methods=["POST"])
def register():
    # [A04: CRYPTOGRAPHIC FAILURES DEMO]
    # Vulnerability: Using MD5 (a broken hash) to store passwords.
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    # CodeQL should detect this as weak cryptographic algorithm (py/weak-cryptographic-algorithm)
    hashed = hashlib.md5(password.encode()).hexdigest()
    try:
        DB_CONN.execute("INSERT INTO users (name, password) VALUES (?, ?)", (username, hashed))
        DB_CONN.commit()
        return {"status": "registered", "stored_hash": hashed}
    except Exception as e:
        return {"error": traceback.format_exc()}, 500

if __name__ == "__main__":
    # [A02: SECURITY MISCONFIGURATION DEMO]
    # Vulnerability: Running Flask in debug mode exposes the interactive debugger.
    app.run(host="0.0.0.0", port=5000, debug=True)
