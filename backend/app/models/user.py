from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from datetime import datetime
from sqlalchemy import func, DateTime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

