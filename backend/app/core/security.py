from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError
from fastapi import Depends, HTTPException
from app.core.config import settings
from app.core.clock import now_utc
from pwdlib import PasswordHash
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from sqlalchemy import select

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def create_access_token(user_id: int) -> str:
    expire = now_utc() + timedelta(minutes=settings.TOKEN_EXPIRED)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_from_token(token: str, db: Session) -> User | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
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

def get_current_admin(c_user: User = Depends(get_current_user)):
    if not c_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return c_user

#for public routes: returns None instead of 401 when there is no valid token
def get_optional_user(token: str | None = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)):
    if not token:
        return None
    return get_user_from_token(token, db)