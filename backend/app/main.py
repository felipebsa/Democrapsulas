from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#routers
from app.routes.auth import router as auth_router
from app.routes.capsule import router as capsule_router
from app.routes.me import router as me_router


app = FastAPI(title="Democrápsulas API")

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
app.include_router(me_router)
