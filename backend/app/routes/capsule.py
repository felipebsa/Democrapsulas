from fastapi import APIRouter

router = APIRouter(prefix="/capsule", tags=["capsule"])

@router.get("/get")
def home():
    return {"message": "successfull home"}
