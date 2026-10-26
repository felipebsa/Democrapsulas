from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.core.clock import now_utc
from app.models.capsule import Capsule
from app.models.user import User
from app.models.vote import Vote
from app.models.favorite import Favorite
from app.schemas.capsule import SchemaCapsuleResponse


def serialize_capsules(db: Session, capsules: list[Capsule], user: User | None) -> list[SchemaCapsuleResponse]:
    now = now_utc()
    ids = [capsule.id for capsule in capsules]

    #a few queries for the whole list instead of one per capsule
    score_query = select(Vote.capsule_id, func.sum(Vote.value)).where(Vote.capsule_id.in_(ids)).group_by(Vote.capsule_id)
    scores = dict(db.execute(score_query).all())
    my_votes = {}
    favorites = set()
    if user is not None:
        vote_query = select(Vote.capsule_id, Vote.value).where(Vote.user_id == user.id, Vote.capsule_id.in_(ids))
        my_votes = dict(db.execute(vote_query).all())
        favorite_query = select(Favorite.capsule_id).where(Favorite.user_id == user.id, Favorite.capsule_id.in_(ids))
        favorites = set(db.execute(favorite_query).scalars().all())

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
            score=scores.get(capsule.id, 0),
            my_vote=my_votes.get(capsule.id),
            is_favorite=capsule.id in favorites,
        ))
    return result


def serialize_capsule(db: Session, capsule: Capsule, user: User | None) -> SchemaCapsuleResponse:
    return serialize_capsules(db, [capsule], user)[0]


def get_capsule_or_404(db: Session, capsule_id: int) -> Capsule:
    capsule = db.get(Capsule, capsule_id)
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    return capsule


#private and hidden capsules only exist for their owner (and admins)
def get_visible_capsule(db: Session, capsule_id: int, user: User | None) -> Capsule:
    capsule = get_capsule_or_404(db, capsule_id)

    is_mine = user is not None and capsule.user_id == user.id
    is_admin = user is not None and user.is_admin
    if (capsule.is_private or capsule.is_hidden) and not (is_mine or is_admin):
        raise HTTPException(status_code=404, detail="Capsule not found")

    return capsule


#the user's vote, favorite or report on a capsule (model is Vote, Favorite or Report)
def find_user_row(db: Session, model, user: User, capsule: Capsule):
    query = select(model).where(model.user_id == user.id, model.capsule_id == capsule.id)
    return db.execute(query).scalar_one_or_none()


def require_open(capsule: Capsule):
    if capsule.open_at > now_utc():
        raise HTTPException(status_code=403, detail="Capsule is not open yet")
