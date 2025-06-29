from fastapi import APIRouter, HTTPException, Depends
from passlib.hash import bcrypt
from jose import jwt
import os
from app.schemas.user import UserRegister, UserLogin
from app.database import db

router = APIRouter()
SECRET_KEY = os.getenv("SECRET", "secret")
ALGORITHM = "HS256"

print("auth.py loaded")

@router.post("/register")
async def register(user: UserRegister):
    print("Registering user:", user.email)
    hashed_password = bcrypt.hash(user.password)
    try:
        result = await db.users.insert_one({
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
        })
        print("Insert result:", result.inserted_id)
    except Exception as e:
        print("DB insert error:", e)
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    return {"message": "User register successfully"}

@router.post("/login")
async def login(user: UserLogin):
    print("Login attempt for:", user.email)
    db_user = await db.users.find_one({"email": user.email})
    print("DB user:", db_user)
    if not db_user:
        raise HTTPException(status_code=401, detail="invalid credentials")
    try:
        if not bcrypt.verify(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="invalid credentials")
    except Exception as e:
        print("Bcrypt error:", e)
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = jwt.encode(
        {"email": user.email},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"token": token}
