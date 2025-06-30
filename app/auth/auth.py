from fastapi import APIRouter, HTTPException
from jose import jwt
from passlib.hash import argon2  
import os

from app.schemas.user import UserRegister, UserLogin
from app.database import db

router = APIRouter(prefix="/auth")
SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM  = "HS256"


@router.post("/register")
async def register(user: UserRegister):
    # Check duplicate email
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = argon2.hash(user.password)
    await db.users.insert_one({
        "name":     user.name,
        "email":    user.email,
        "password": hashed_pw,
    })
    return {"message": "User registered successfully"}


@router.post("/login")
async def login(user: UserLogin):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not argon2.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"email": user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token}
