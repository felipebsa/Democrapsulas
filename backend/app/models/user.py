from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from datetime import datetime
from sqlalchemy import func, DateTime, String, false
from app.core.constants import USERNAME_MAX_LENGTH

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(USERNAME_MAX_LENGTH), unique=True)
    password_hash: Mapped[str] = mapped_column()
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=false())
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
