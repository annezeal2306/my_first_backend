from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, select, insert, delete, update
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import NoResultFound
from fastapi.middleware.cors import CORSMiddleware
# --- 1. DATABASE SETUP ---

# Define the database file
DATABASE_URL = "sqlite:///./tasks.db"

# Create the SQLAlchemy "engine"
# This is the main connection point to our database
engine = create_engine(
    DATABASE_URL, 
    # This setting is required for SQLite when used with FastAPI
    connect_args={"check_same_thread": False} 
)

# Create a "SessionLocal" class
# Each instance of this class will be a new database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a "Base" class
# Our database model (the 'Task' table) will inherit from this
Base = declarative_base()

origins = [
    "http://localhost:5173",
]
# --- 2. DEFINE THE 'tasks' TABLE MODEL ---

# This class defines the 'tasks' table in our database
class TaskTable(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    completed = Column(Boolean, default=False)

# This function creates the actual table in the database
# We will run this function from our code one time
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

# --- 3. PYDANTIC MODELS (for API) ---

# This is the Pydantic model for CREATING a task
# Notice it doesn't have an 'id' - the database will create that
class TaskCreate(BaseModel):
    title: str
    completed: bool = False

# This is the Pydantic model for READING/UPDATING a task
# It includes the 'id'
class Task(BaseModel):
    id: int
    title: str
    completed: bool

    # This 'Config' class allows the model to be created
    # from our SQLAlchemy database object
    class Config:
        orm_mode = True # In Pydantic v2, this is from_attributes = True

# --- 4. FASTAPI APP ---
app = FastAPI()

# --- 5. UPDATED API ENDPOINTS ---
# Notice how they now use the database session (db: Session)

@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    with SessionLocal() as db:
        # Create a new dictionary with the data
        task_data = task.model_dump() # In Pydantic v1, this is task.dict()
        
        # Create the insert statement
        stmt = insert(TaskTable).values(**task_data)
        
        # Execute and get the new ID
        result = db.execute(stmt)
        db.commit() # Save the changes
        
        new_id = result.inserted_primary_key[0]
        
        # Return the newly created task
        return {"id": new_id, **task_data}

@app.get("/tasks", response_model=list[Task])
def get_tasks():
    with SessionLocal() as db:
        # Create the select statement
        stmt = select(TaskTable)
        
        # Execute and fetch all results
        tasks = db.scalars(stmt).all()
        return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    with SessionLocal() as db:
        try:
            # Create the select statement
            stmt = select(TaskTable).where(TaskTable.id == task_id)
            
            # Execute and get one result
            task = db.scalars(stmt).one()
            return task
        except NoResultFound:
            # If 'one()' finds nothing, it raises an error
            raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskCreate):
    with SessionLocal() as db:
        # First, check if the task exists
        get_task(task_id) # This will raise 404 if not found
        
        # Create the update statement
        stmt = (
            update(TaskTable)
            .where(TaskTable.id == task_id)
            .values(**task.model_dump()) # In Pydantic v1, this is task.dict()
        )
        
        db.execute(stmt)
        db.commit() # Save the changes
        
        # Return the updated task
        return {"id": task_id, **task.model_dump()}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with SessionLocal() as db:
        # First, check if the task exists
        get_task(task_id) # This will raise 404 if not found
        
        # Create the delete statement
        stmt = delete(TaskTable).where(TaskTable.id == task_id)
        
        db.execute(stmt)
        db.commit() # Save the changes
        
        return {"status": "success", "message": f"Task {task_id} deleted"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)