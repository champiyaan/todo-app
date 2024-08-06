from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

class User(BaseModel):
    username: str
    password: str

class Todo(BaseModel):
    task: str
    due_date: datetime = None
    completed: bool = False

@app.on_event("startup")
async def startup():
    try:
        app.state.pool = await asyncpg.create_pool(DATABASE_URL, max_size=10)
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

@app.post("/login")
async def login(user: User):
    query = "SELECT * FROM users WHERE username = $1 AND password = $2"
    try:
        async with app.state.pool.acquire() as connection:
            result = await connection.fetchrow(query, user.username, user.password)
            if not result:
                raise HTTPException(status_code=400, detail="Invalid credentials")
        return {"message": "Login successful"}
    except Exception as e:
        print(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/todos")
async def create_todo(todo: Todo):
    query = "INSERT INTO todos (task, due_date, completed) VALUES ($1, $2, $3) RETURNING id"
    try:
        async with app.state.pool.acquire() as connection:
            current_time = datetime.utcnow()
            todo_id = await connection.fetchval(query, todo.task, current_time, todo.completed)
            return {"id": todo_id, "created": current_time, **todo.dict()}
    except Exception as e:
        print(f"Error creating todo: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/todos")
async def get_todos():
    query = "SELECT id, task, due_date AS created, completed FROM todos"
    try:
        async with app.state.pool.acquire() as connection:
            todos = await connection.fetch(query)
            return todos
    except Exception as e:
        print(f"Error fetching todos: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, todo: Todo):
    query = "UPDATE todos SET task = $1, due_date = $2, completed = $3 WHERE id = $4"
    try:
        async with app.state.pool.acquire() as connection:
            current_time = datetime.utcnow()
            await connection.execute(query, todo.task, current_time, todo.completed, todo_id)
            return {"message": "Todo updated successfully"}
    except Exception as e:
        print(f"Error updating todo: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    query = "DELETE FROM todos WHERE id = $1"
    try:
        async with app.state.pool.acquire() as connection:
            await connection.execute(query, todo_id)
            return {"message": "Todo deleted successfully"}
    except Exception as e:
        print(f"Error deleting todo: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
