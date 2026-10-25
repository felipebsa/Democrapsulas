from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token, hash_password, get_current_user
from app.schemas.user import SchemaUserCreate, SchemaUserResponse
from sqlalchemy import select


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    query = select(User).where(User.name == form_data.username)
    db_user = db.execute(query).scalar_one_or_none()

    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail=("Invalid credentials"))

    token = create_access_token(db_user.id)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", status_code=201, response_model=SchemaUserResponse)
def create_user(user: SchemaUserCreate, db: Session = Depends(get_db)):
    query = select(User).where(User.name == user.name)
    existing_user = db.execute(query).scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=409, detail="username already registered")
    hash_created = hash_password(user.password)
    post_user = User(
        name = user.name,
        password_hash = hash_created
    )
    db.add(post_user)
    db.commit()
    db.refresh(post_user)
    return post_user

@router.get("/me", response_model=SchemaUserResponse)
def me(c_user=Depends(get_current_user)):
    return c_user