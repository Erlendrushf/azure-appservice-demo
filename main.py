"""
FastAPI Demo Application for Azure App Service
This application demonstrates various API endpoints with automatic Swagger documentation.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import random
import uuid

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Azure App Service Demo API",
    description="A comprehensive demo API showcasing FastAPI capabilities",
    version="1.0.0",
    docs_url="/swagger",  # Swagger UI endpoint
    redoc_url="/redoc",   # ReDoc endpoint
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

class Quote(BaseModel):
    id: str
    text: str
    author: str
    category: str

class WeatherResponse(BaseModel):
    city: str
    temperature: float
    condition: str
    humidity: int
    timestamp: str

class Task(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    completed: bool = False
    created_at: Optional[str] = None

class UserProfile(BaseModel):
    username: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None

# In-memory storage (for demo purposes)
tasks_db = []
quotes_db = [
    {"id": str(uuid.uuid4()), "text": "The only way to do great work is to love what you do.", "author": "Steve Jobs", "category": "motivation"},
    {"id": str(uuid.uuid4()), "text": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs", "category": "innovation"},
    {"id": str(uuid.uuid4()), "text": "Code is like humor. When you have to explain it, it's bad.", "author": "Cory House", "category": "programming"},
    {"id": str(uuid.uuid4()), "text": "First, solve the problem. Then, write the code.", "author": "John Johnson", "category": "programming"},
    {"id": str(uuid.uuid4()), "text": "The best way to predict the future is to invent it.", "author": "Alan Kay", "category": "innovation"},
]

# Root endpoint
@app.get("/", tags=["General"])
async def root():
    """
    Root endpoint - Welcome message
    """
    return {
        "message": "Welcome to Azure App Service Demo API!",
        "documentation": "/swagger",
        "health_check": "/health",
        "endpoints": {
            "quotes": "/api/quotes",
            "weather": "/api/weather/{city}",
            "tasks": "/api/tasks",
            "random_user": "/api/random-user",
            "uuid_generator": "/api/uuid"
        }
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

# Quotes API
@app.get("/api/quotes", response_model=List[Quote], tags=["Quotes"])
async def get_quotes(category: Optional[str] = Query(None, description="Filter by category")):
    """
    Get inspirational quotes. Optionally filter by category.
    
    Categories: motivation, innovation, programming
    """
    if category:
        filtered_quotes = [q for q in quotes_db if q["category"] == category]
        return filtered_quotes
    return quotes_db

@app.get("/api/quotes/random", response_model=Quote, tags=["Quotes"])
async def get_random_quote():
    """
    Get a random inspirational quote
    """
    return random.choice(quotes_db)

@app.get("/api/quotes/{quote_id}", response_model=Quote, tags=["Quotes"])
async def get_quote_by_id(quote_id: str):
    """
    Get a specific quote by ID
    """
    quote = next((q for q in quotes_db if q["id"] == quote_id), None)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote

# Weather API (Mock data)
@app.get("/api/weather/{city}", response_model=WeatherResponse, tags=["Weather"])
async def get_weather(city: str):
    """
    Get mock weather data for a city
    """
    conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy", "Partly Cloudy"]
    
    return WeatherResponse(
        city=city.title(),
        temperature=round(random.uniform(-10, 35), 1),
        condition=random.choice(conditions),
        humidity=random.randint(30, 90),
        timestamp=datetime.now().isoformat()
    )

# Tasks API (CRUD operations)
@app.get("/api/tasks", response_model=List[Task], tags=["Tasks"])
async def get_tasks(completed: Optional[bool] = Query(None, description="Filter by completion status")):
    """
    Get all tasks. Optionally filter by completion status.
    """
    if completed is not None:
        return [task for task in tasks_db if task.completed == completed]
    return tasks_db

@app.post("/api/tasks", response_model=Task, status_code=201, tags=["Tasks"])
async def create_task(task: Task):
    """
    Create a new task
    """
    task.id = str(uuid.uuid4())
    task.created_at = datetime.now().isoformat()
    task_dict = task.model_dump()
    tasks_db.append(task_dict)
    return task_dict

@app.get("/api/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def get_task(task_id: str):
    """
    Get a specific task by ID
    """
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/api/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def update_task(task_id: str, task_update: Task):
    """
    Update an existing task
    """
    task_index = next((i for i, t in enumerate(tasks_db) if t["id"] == task_id), None)
    if task_index is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_update.id = task_id
    task_update.created_at = tasks_db[task_index]["created_at"]
    tasks_db[task_index] = task_update.model_dump()
    return tasks_db[task_index]

@app.delete("/api/tasks/{task_id}", tags=["Tasks"])
async def delete_task(task_id: str):
    """
    Delete a task
    """
    task_index = next((i for i, t in enumerate(tasks_db) if t["id"] == task_id), None)
    if task_index is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    deleted_task = tasks_db.pop(task_index)
    return {"message": "Task deleted successfully", "task": deleted_task}

# Random User Generator API
@app.get("/api/random-user", response_model=UserProfile, tags=["Utilities"])
async def get_random_user():
    """
    Generate a random user profile
    """
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    username = f"{first_name.lower()}.{last_name.lower()}"
    
    return UserProfile(
        username=username,
        email=f"{username}@example.com",
        full_name=f"{first_name} {last_name}",
        avatar_url=f"https://ui-avatars.com/api/?name={first_name}+{last_name}"
    )

# UUID Generator API
@app.get("/api/uuid", tags=["Utilities"])
async def generate_uuid(count: int = Query(1, ge=1, le=100, description="Number of UUIDs to generate")):
    """
    Generate one or more UUIDs
    """
    return {
        "count": count,
        "uuids": [str(uuid.uuid4()) for _ in range(count)]
    }

# Statistics API
@app.get("/api/stats", tags=["General"])
async def get_stats():
    """
    Get application statistics
    """
    return {
        "total_tasks": len(tasks_db),
        "completed_tasks": len([t for t in tasks_db if t.get("completed", False)]),
        "pending_tasks": len([t for t in tasks_db if not t.get("completed", False)]),
        "total_quotes": len(quotes_db),
        "uptime": "Running",
        "timestamp": datetime.now().isoformat()
    }

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
