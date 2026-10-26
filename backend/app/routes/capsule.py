from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.capsule import Capsule
from app.models.vote import Vote
from app.models.favorite import Favorite
from app.models.report import Report
from app.core.config import settings
from app.core.constants import Hall
from app.core.profanity import contains_bad_words
from app.core.security import get_current_user, get_optional_user
from app.schemas.capsule import SchemaCapsuleCreate, SchemaCapsuleResponse, SchemaVote, SchemaReport
from app.services.capsule import now_utc, serialize_capsule, serialize_capsules, get_visible_capsule, require_open

router = APIRouter(prefix="/capsules", tags=["capsules"])

@router.post("", status_code=201, response_model=SchemaCapsuleResponse)
def create_capsule(capsule: SchemaCapsuleCreate, db: Session = Depends(get_db), c_user=Depends(get_current_user)):
    now = now_utc()

    if capsule.open_at <= now:
        raise HTTPException(status_code=422, detail="open_at must be in the future")

    if contains_bad_words(capsule.title) or contains_bad_words(capsule.content):
        raise HTTPException(status_code=422, detail="Capsule contains inappropriate words")

    last_query = select(Capsule.created).where(Capsule.user_id == c_user.id).order_by(Capsule.created.desc()).limit(1)
    last_created = db.execute(last_query).scalar_one_or_none()
    if last_created:
        wait = settings.CAPSULE_COOLDOWN_SECONDS - (now - last_created).total_seconds()
        if wait > 0:
            raise HTTPException(status_code=429, detail=f"Wait {int(wait) + 1} seconds before creating another capsule")

    count_query = select(func.count()).select_from(Capsule).where(
        Capsule.user_id == c_user.id,
        Capsule.created >= now - timedelta(days=1),
    )
    if db.execute(count_query).scalar_one() >= settings.CAPSULES_PER_DAY:
        raise HTTPException(status_code=429, detail="Daily capsule limit reached")

    new_capsule = Capsule(user_id=c_user.id, **capsule.model_dump())
    db.add(new_capsule)
    db.commit()
    db.refresh(new_capsule)
    return serialize_capsule(db, new_capsule, c_user)

#random sample of public capsules for one hall (opened or not)
@router.get("", response_model=list[SchemaCapsuleResponse])
def list_hall_capsules(hall: Hall, db: Session = Depends(get_db), c_user=Depends(get_optional_user)):
    query = (
        select(Capsule)
        .where(Capsule.hall == hall, Capsule.is_private == False, Capsule.is_hidden == False)
        .order_by(func.random())
        .limit(settings.HALL_CAPSULE_LIMIT)
    )
    capsules = db.execute(query).scalars().all()
    return serialize_capsules(db, capsules, c_user)

@router.get("/{capsule_id}", response_model=SchemaCapsuleResponse)
def get_capsule(capsule_id: int, db: Session = Depends(get_db), c_user=Depends(get_optional_user)):
    capsule = get_visible_capsule(db, capsule_id, c_user)
    return serialize_capsule(db, capsule, c_user)

@router.delete("/{capsule_id}", status_code=204)
def delete_capsule(capsule_id: int, db: Session = Depends(get_db), c_user=Depends(get_current_user)):
    capsule = db.get(Capsule, capsule_id)
    if not capsule or capsule.user_id != c_user.id:
        raise HTTPException(status_code=404, detail="Capsule not found")

    db.delete(capsule)
    db.commit()
    return Response(status_code=204)

#votes, favorites and reports only work after the capsule is open
@router.put("/{capsule_id}/vote", response_model=SchemaCapsuleResponse)
def vote_capsule(capsule_id: int, vote: SchemaVote, db: Session = Depends(get_db), c_user=Depends(get_current_user)):
    capsule = get_visible_capsule(db, capsule_id, c_user)
    require_open(capsule)

    query = select(Vote).where(Vote.user_id == c_user.id, Vote.capsule_id == capsule.id)
    existing_vote = db.execute(query).scalar_one_or_none()
    if existing_vote:
        existing_vote.value = vote.value
    else:
        db.add(Vote(user_id=c_user.id, capsule_id=capsule.id, value=vote.value))
    db.commit()
    return serialize_capsule(db, capsule, c_user)

@router.delete("/{capsule_id}/vote", response_model=SchemaCapsuleResponse)
def remove_vote(capsule_id: int, db: Session = Depends(get_db), c_user=Depends(get_current_user)):
    capsule = get_visible_capsule(db, capsule_id, c_user)

    query = select(Vote).where(Vote.user_id == c_user.id, Vote.capsule_id == capsule.id)
    existing_vote = db.execute(query).scalar_one_or_none()
    if existing_vote:
        db.delete(existing_vote)
        db.commit()
    return serialize_capsule(db, capsule, c_user)

@router.put("/{capsule_id}/favorite", response_model=SchemaCapsuleResponse)
def favorite_capsule(capsule_id: int, db: Session = Depends(get_db), c_user=Depends(get_current_user)):
    capsule = get_visible_capsule(db, capsule_id, c_user)
    require_open(capsule)

    query = select(Favorite).where(Favorite.user_id == c_user.id, Favorite.capsule_id == capsule.id)
    if not db.execute(query).scalar_one_or_none():
        db.add(Favorite(user_id=c_user.id, capsule_id=capsule.id))
        db.commit()
    return serialize_capsule(db, capsule, c_user)

@router.delete("/{capsule_id}/favorite", response_model=SchemaCapsuleResponse)
def unfavorite_capsule(capsule_id: int, db: Session = Depends(get_db), c_user=Depends(get_current_user)):
    capsule = get_visible_capsule(db, capsule_id, c_user)

    query = select(Favorite).where(Favorite.user_id == c_user.id, Favorite.capsule_id == capsule.id)
    favorite = db.execute(query).scalar_one_or_none()
    if favorite:
        db.delete(favorite)
        db.commit()
    return serialize_capsule(db, capsule, c_user)

@router.post("/{capsule_id}/report", status_code=201)
def report_capsule(capsule_id: int, report: SchemaReport, db: Session = Depends(get_db), c_user=Depends(get_current_user)):
    capsule = get_visible_capsule(db, capsule_id, c_user)
    require_open(capsule)

    query = select(Report).where(Report.user_id == c_user.id, Report.capsule_id == capsule.id)
    if db.execute(query).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Capsule already reported")

    db.add(Report(user_id=c_user.id, capsule_id=capsule.id, reason=report.reason))
    db.flush()

    count_query = select(func.count()).select_from(Report).where(Report.capsule_id == capsule.id)
    if db.execute(count_query).scalar_one() >= settings.REPORTS_TO_HIDE:
        capsule.is_hidden = True
    db.commit()
    return {"detail": "Capsule reported"}
