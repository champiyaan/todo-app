from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncpg
import os

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
