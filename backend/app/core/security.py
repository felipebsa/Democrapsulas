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
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_from_token(token: str, db: Session) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (InvalidTokenError, TypeError, ValueError):
        return None

    user_query = select(User).where(User.id==user_id)
    return db.execute(user_query).scalars().first()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_user_from_token(token, db)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

#for public routes: returns None instead of 401 when there is no valid token
def get_optional_user(token: str | None = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)):
    if not token:
        return None
    return get_user_from_token(token, db)