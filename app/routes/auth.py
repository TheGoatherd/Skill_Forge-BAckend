from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
from jose import jwt
from argon2 import PasswordHasher
from app.database.mongodb import get_db  # FIXED: import get_db from correct location
from motor.motor_asyncio import AsyncIOMotorDatabase

class User(BaseModel):
    email: str
    password: str

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"

# Create a password hasher instance
ph = PasswordHasher()

@router.post("/Register")
async def register(user: User, db: AsyncIOMotorDatabase = Depends(get_db)):
    if not user.email.endswith("@gmail.com"):
        raise HTTPException(status_code=400, detail="Email is not valid")

    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hash_pass = ph.hash(user.password)
    await db.users.insert_one({
        "email": user.email,
        "password": hash_pass
    })

    return {"message": "User registered successfully"}

@router.post("/Login")
async def login(user: User, db: AsyncIOMotorDatabase = Depends(get_db)):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    try:
        ph.verify(db_user["password"], user.password)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = jwt.encode({"email": user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"message": "Login successful", "token": token}


