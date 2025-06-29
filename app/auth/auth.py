from fastapi import APIRouter, HTTPException, Depends
from passlib.hash import bcrypt
from jose import jwt
import os
from app.schemas.user import UserRegister, UserLogin
from app.database import db

router = APIRouter()
SECRET_KEY = os.getenv("SECRET", "secret")
ALGORITHM = "HS256"

@router.post("/register")
async def register(user: UserRegister):
    if not user.email.endswith("@email.com"):
        raise HTTPException(status_code=400, detail="Email must end with @email.com")
    hashed_password = bcrypt.hash(user.password)
    await db.users.insert_one({
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
    })
    return {"message": "User register successfully"}

@router.post("/login")
async def login(user: UserLogin):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=401, detail="invalid credentials")
    try:
        if not bcrypt.verify(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="invalid credentials")
    except Exception:
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = jwt.encode(
        {"email": user.email},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"token": token}
