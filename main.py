from fastapi import FastAPI, HTTPException
import sqlite3
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy groceries", 0))
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Clean room", 0))
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Study FastAPI", 1))
        conn.commit()
    conn.close()

init_db()

app = FastAPI()

@app.get("/")
def root():
    """Returns basic info about the API"""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    """Check if the server is running"""
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    """Get all tasks"""
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(task) for task in tasks]

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """Get a single task by ID"""
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return dict(task)

@app.post("/tasks", status_code=201)
def create_task(task: dict):
    """Create a new task"""
    if "title" not in task or not task["title"]:
        raise HTTPException(status_code=400, detail="Title is required")
    conn = get_db()
    cursor = conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task["title"], 0))
    conn.commit()
    new_task = conn.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return dict(new_task)

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updates: dict):
    """Update a task's title or done status"""
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    title = updates.get("title", task["title"])
    done = updates.get("done", task["done"])
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    conn.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (title, done, task_id))
    conn.commit()
    updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(updated)

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    """Delete a task by ID"""
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

@app.post("/auth/signup", status_code=201)
def signup(data: dict):
    if "email" not in data or "password" not in data:
        raise HTTPException(status_code=400, detail="Email and password are required")
    response = supabase.auth.sign_up({
        "email": data["email"],
        "password": data["password"]
    })
    return {"user": response.user}

@app.post("/auth/login")
def login(data: dict):
    if "email" not in data or "password" not in data:
        raise HTTPException(status_code=400, detail="Email and password are required")
    response = supabase.auth.sign_in_with_password({
        "email": data["email"],
        "password": data["password"]
    })
    if not response.user:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token
    }
@app.get("/public/info")
def public_info():
    """Public endpoint - no auth needed"""
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile")
def profile(authorization: str = None):
    """Protected endpoint - requires auth token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")
    token = authorization.replace("Bearer ", "")
    response = supabase.auth.get_user(token)
    if not response.user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {
        "id": response.user.id,
        "email": response.user.email,
        "created_at": response.user.created_at
    }
