from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.capsule import Capsule
from app.models.user import User
from app.schemas.capsule import SchemaCapsuleResponse


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def serialize_capsules(db: Session, capsules: list[Capsule], user: User | None) -> list[SchemaCapsuleResponse]:
    now = now_utc()
    result = []
    for capsule in capsules:
        is_open = capsule.open_at <= now
        is_mine = user is not None and capsule.user_id == user.id
        reveal = is_open or is_mine
        result.append(SchemaCapsuleResponse(
            id=capsule.id,
            hall=capsule.hall,
            is_private=capsule.is_private,
            is_open=is_open,
            is_mine=is_mine,
            open_at=capsule.open_at,
            created=capsule.created,
            title=capsule.title if reveal else None,
            content=capsule.content if reveal else None,
            author=capsule.author.name if reveal else None,
        ))
    return result


def serialize_capsule(db: Session, capsule: Capsule, user: User | None) -> SchemaCapsuleResponse:
    return serialize_capsules(db, [capsule], user)[0]


#private and hidden capsules only exist for their owner (and admins)
def get_visible_capsule(db: Session, capsule_id: int, user: User | None) -> Capsule:
    capsule = db.get(Capsule, capsule_id)
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")

    is_mine = user is not None and capsule.user_id == user.id
    is_admin = user is not None and user.is_admin
    if (capsule.is_private or capsule.is_hidden) and not (is_mine or is_admin):
        raise HTTPException(status_code=404, detail="Capsule not found")

    return capsule


def require_open(capsule: Capsule):
    if capsule.open_at > now_utc():
        raise HTTPException(status_code=403, detail="Capsule is not open yet")
