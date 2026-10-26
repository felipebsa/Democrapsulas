from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.capsule import Capsule
from app.core.security import get_current_user
from app.schemas.capsule import SchemaCapsuleResponse
from app.services.capsule import serialize_capsules

router = APIRouter(prefix="/me", tags=["me"])

#all capsules of the logged user, including private ones
@router.get("/capsules", response_model=list[SchemaCapsuleResponse])
def my_capsules(db: Session = Depends(get_db), c_user=Depends(get_current_user)):
    query = select(Capsule).where(Capsule.user_id == c_user.id).order_by(Capsule.created.desc())
    capsules = db.execute(query).scalars().all()
    return serialize_capsules(db, capsules, c_user)
