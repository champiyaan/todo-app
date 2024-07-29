from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg
import json

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

# Database connection details
DATABASE_URL = "postgresql://test:test@localhost/testdb"

class User(BaseModel):
    username: str
    password: str

@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)

@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()

@app.post("/login")
async def login(user: User):
    print(f"Received login request: {user.json()}")
    query = "SELECT * FROM users WHERE username = $1 AND password = $2"
    async with app.state.pool.acquire() as connection:
        result = await connection.fetchrow(query, user.username, user.password)
        if not result:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful"}
