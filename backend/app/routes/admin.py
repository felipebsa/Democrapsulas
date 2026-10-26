from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.capsule import Capsule
from app.models.report import Report
from app.core.security import get_current_admin
from app.schemas.admin import SchemaAdminCapsule

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])

def get_capsule_or_404(db: Session, capsule_id: int) -> Capsule:
    capsule = db.get(Capsule, capsule_id)
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    return capsule

def to_admin_capsule(db: Session, capsule: Capsule) -> SchemaAdminCapsule:
    reasons_query = select(Report.reason).where(Report.capsule_id == capsule.id).order_by(Report.created)
    reasons = db.execute(reasons_query).scalars().all()
    return SchemaAdminCapsule(
        id=capsule.id,
        hall=capsule.hall,
        title=capsule.title,
        content=capsule.content,
        author=capsule.author.name,
        is_private=capsule.is_private,
        is_hidden=capsule.is_hidden,
        open_at=capsule.open_at,
        created=capsule.created,
        reports=len(reasons),
        reasons=[reason for reason in reasons if reason],
    )

#hidden: waiting for review; reported: has reports but is still visible
@router.get("/capsules", response_model=list[SchemaAdminCapsule])
def list_capsules(status: Literal["hidden", "reported"] = "hidden", db: Session = Depends(get_db)):
    if status == "hidden":
        query = select(Capsule).where(Capsule.is_hidden == True)
    else:
        reported = select(Report.capsule_id)
        query = select(Capsule).where(Capsule.is_hidden == False, Capsule.id.in_(reported))

    capsules = db.execute(query.order_by(Capsule.created.desc())).scalars().all()
    return [to_admin_capsule(db, capsule) for capsule in capsules]

#capsule is fine: show it again and clear its reports
@router.post("/capsules/{capsule_id}/approve", response_model=SchemaAdminCapsule)
def approve_capsule(capsule_id: int, db: Session = Depends(get_db)):
    capsule = get_capsule_or_404(db, capsule_id)
    capsule.is_hidden = False
    db.execute(delete(Report).where(Report.capsule_id == capsule.id))
    db.commit()
    return to_admin_capsule(db, capsule)

@router.post("/capsules/{capsule_id}/hide", response_model=SchemaAdminCapsule)
def hide_capsule(capsule_id: int, db: Session = Depends(get_db)):
    capsule = get_capsule_or_404(db, capsule_id)
    capsule.is_hidden = True
    db.commit()
    return to_admin_capsule(db, capsule)

@router.delete("/capsules/{capsule_id}", status_code=204)
def delete_capsule(capsule_id: int, db: Session = Depends(get_db)):
    capsule = get_capsule_or_404(db, capsule_id)
    db.delete(capsule)
    db.commit()
    return Response(status_code=204)
