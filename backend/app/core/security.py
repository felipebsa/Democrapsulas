from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError
from fastapi import Depends, HTTPException
from app.core.config import settings
from pwdlib import PasswordHash
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from sqlalchemy import select

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.TOKEN_EXPIRED

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user_query = select(User).where(User.id==user_id)
    user = db.execute(user_query).scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user