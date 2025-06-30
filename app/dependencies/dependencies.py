from fastapi import Request, HTTPException
from jose import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"

# ✅ Exportable function
# get_db is defined in app.database.mongodb, import it where needed

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
