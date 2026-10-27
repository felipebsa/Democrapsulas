from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.capsule import Capsule
from app.models.vote import Vote
from app.core.config import settings
from app.core.constants import HALLS, Hall
from app.core.security import get_optional_user
from app.schemas.capsule import SchemaCapsuleResponse
from app.schemas.stats import SchemaStats
from app.core.clock import now_utc
from app.services.capsule import PUBLIC, serialize_capsules

router = APIRouter(tags=["stats"])

def count(db: Session, query) -> int:
    return db.execute(query).scalar_one()

#open public capsules with positive score, best first (ties: opened first)
@router.get("/ranking", response_model=list[SchemaCapsuleResponse])
def ranking(
    hall: Hall | None = None,
    limit: int = Query(default=settings.RANKING_LIMIT, ge=1, le=100),
    db: Session = Depends(get_db),
    c_user=Depends(get_optional_user),
):
    scores = select(Vote.capsule_id, func.sum(Vote.value).label("score")).group_by(Vote.capsule_id).subquery()
    query = (
        select(Capsule)
        .join(scores, scores.c.capsule_id == Capsule.id)
        .where(*PUBLIC, Capsule.open_at <= now_utc(), scores.c.score > 0)
        .order_by(scores.c.score.desc(), Capsule.open_at.asc())
        .limit(limit)
    )
    if hall:
        query = query.where(Capsule.hall == hall)

    capsules = db.execute(query).scalars().all()
    return serialize_capsules(db, capsules, c_user)

@router.get("/stats", response_model=SchemaStats)
def stats(db: Session = Depends(get_db)):
    now = now_utc()
    capsule_count = select(func.count()).select_from(Capsule)

    per_hall_query = select(Capsule.hall, func.count()).where(*PUBLIC).group_by(Capsule.hall)
    per_hall = {hall: 0 for hall in HALLS}
    per_hall.update(dict(db.execute(per_hall_query).all()))

    return SchemaStats(
        users=count(db, select(func.count()).select_from(User)),
        capsules=count(db, capsule_count),
        open_capsules=count(db, capsule_count.where(Capsule.open_at <= now)),
        waiting_capsules=count(db, capsule_count.where(Capsule.open_at > now)),
        capsules_per_hall=per_hall,
        votes=count(db, select(func.count()).select_from(Vote)),
    )
