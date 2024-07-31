from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import asyncpg
import os
from datetime import datetime

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

# Allow all origins (you can specify particular origins if needed)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection details from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

class TodoCreate(BaseModel):
    task: str
    due_date: Optional[str] = None
    completed: bool

class TodoUpdate(BaseModel):
    task: Optional[str] = None
    due_date: Optional[str] = None
    completed: Optional[bool] = None

@app.on_event("startup")
async def startup():
    try:
        app.state.pool = await asyncpg.create_pool(DATABASE_URL, max_size=10)  # Adjust max_size as needed
        print("Database connection pool created successfully")
    except Exception as e:
        print(f"Error creating connection pool: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to the database")

@app.on_event("shutdown")
async def shutdown():
    try:
        await app.state.pool.close()
        print("Database connection pool closed")
    except Exception as e:
        print(f"Error closing connection pool: {e}")

@app.post("/todos")
async def create_todo(todo: TodoCreate):
    query = """INSERT INTO todos (task, due_date, completed) VALUES ($1, $2, $3) RETURNING id"""
    
    try:
        due_date = datetime.now() if not todo.due_date else datetime.fromisoformat(todo.due_date)
        async with app.state.pool.acquire() as connection:
            result = await connection.fetchrow(query, todo.task, due_date, todo.completed)
            return {"id": result["id"], "message": "Todo created successfully"}
    except Exception as e:
        print(f"Error creating todo: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/todos")
async def get_todos():
    query = """SELECT * FROM todos"""
    try:
        async with app.state.pool.acquire() as connection:
            result = await connection.fetch(query)
            return result
    except Exception as e:
        print(f"Error fetching todos: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, todo: TodoUpdate):
    update_query = """UPDATE todos SET 
                      task = COALESCE($1, task), 
                      due_date = COALESCE($2, due_date), 
                      completed = COALESCE($3, completed) 
                      WHERE id = $4"""

    try:
        due_date = datetime.now() if not todo.due_date else datetime.fromisoformat(todo.due_date)
        async with app.state.pool.acquire() as connection:
            await connection.execute(update_query, todo.task, due_date, todo.completed, todo_id)
            return {"message": "Todo updated successfully"}
    except Exception as e:
        print(f"Error updating todo: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    query = """DELETE FROM todos WHERE id = $1"""
    try:
        async with app.state.pool.acquire() as connection:
            await connection.execute(query, todo_id)
            return {"message": "Todo deleted successfully"}
    except Exception as e:
        print(f"Error deleting todo: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
