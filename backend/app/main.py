from fastapi import FastAPI
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

#routers
from app.routes.auth import router as auth_router
from app.routes.capsule import router as capsule_router

#models
# from app.models.user import User
# from app.models.capsule import Capsule


app = FastAPI()

#settings cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#include routers
app.include_router(auth_router)
app.include_router(capsule_router)