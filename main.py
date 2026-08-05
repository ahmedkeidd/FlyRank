from fastapi import FastAPI, HTTPException

app = FastAPI()

tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Clean room", "done": False},
    {"id": 3, "title": "Study FastAPI", "done": True},
]

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
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """Get a single task by ID"""
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks", status_code=201)
def create_task(task: dict):
    """Create a new task"""
    if "title" not in task or not task["title"]:
        raise HTTPException(status_code=400, detail="Title is required")
    new_task = {
        "id": len(tasks) + 1,
        "title": task["title"],
        "done": False
    }
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updates: dict):
    """Update a task's title or done status"""
    for task in tasks:
        if task["id"] == task_id:
            if "title" in updates and updates["title"]:
                task["title"] = updates["title"]
            if "done" in updates:
                task["done"] = updates["done"]
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    """Delete a task by ID"""
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")