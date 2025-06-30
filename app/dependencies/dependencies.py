from fastapi import Request, HTTPException
from jose import jwt
import os
from app.database.mongodb import db

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"

# ✅ Exportable function
async def get_db():
    return db

# ✅ Exportable auth dependency
async def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer"):
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
