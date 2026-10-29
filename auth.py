import os
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def require_login(credentials: HTTPBasicCredentials = Depends(security)):
    password = os.environ.get("LIFE_OS_PASSWORD")
    if not password:
        raise HTTPException(status_code=500, detail="LIFE_OS_PASSWORD is not set")
    user_ok = secrets.compare_digest(credentials.username.encode(), b"me")
    pass_ok = secrets.compare_digest(credentials.password.encode(), password.encode())
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=401, detail="Wrong login",
            headers={"WWW-Authenticate": "Basic"},
        )