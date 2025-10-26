from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

app = FastAPI()

# Create a simple "database" as a Python list of dictionaries
fake_tasks_db = [
    {"id": 1, "title": "Learn Python", "completed": True},
    {"id": 2, "title": "Build an API", "completed": True},
    {"id": 3, "title": "Take a break", "completed": False},
]

class Task(BaseModel):
    title: str
    completed: bool
# The root endpoint from before
@app.get("/")
def read_root():
    return {"Hello": "Welcome to your task list!"}


# A NEW endpoint to get all tasks
@app.get("/tasks")
def get_tasks():
    return fake_tasks_db

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    # Loop through the database
    for task in fake_tasks_db:
        if task["id"] == task_id:
            return task
    
    # If the loop finishes without finding the task, raise an error
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks")
def create_task(task: Task):
    new_id=len(fake_tasks_db) + 1
    new_task={"id":new_id, "title":task.title, "completed":task.completed}
    
    fake_tasks_db.append(new_task)
    return new_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    task_to_delete=None
    for task in fake_tasks_db:
        if task["id"] == task_id:
            task_to_delete=task
            break
    if task_to_delete is None:
        raise HTTPException(status_code=404, detail="Task not found")
    fake_tasks_db.remove(task_to_delete)
    return {"status":"success","message": f"Task {task_id} deleted"}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task):
    task_to_update = None
    for i,task in enumerate(fake_tasks_db):
        if task["id"] == task_id:
            task_to_update = {
                "id": task_id,
                "title": updated_task.title,
                "completed": updated_task.completed
            }
            fake_tasks_db[i] = task_to_update
            break
    if task_to_update is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_to_update
# @app.get("/tasks/{task_id}")
# def read_task(task_id: int):
#     for task in fake_tasks_db:
#         if task["id"] == task_id:
#             return task
#     raise HTTPException(status_code=404, detail="Task not found")
