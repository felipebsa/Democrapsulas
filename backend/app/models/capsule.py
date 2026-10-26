from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, String, ForeignKey, DateTime
from app.database import Base
from app.models.user import User
from datetime import datetime

class Capsule(Base):
    __tablename__ = "capsules"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    hall: Mapped[str] = mapped_column(String(20), index=True)
    title: Mapped[str] = mapped_column(String(80))
    content: Mapped[str] = mapped_column(String(1000))
    is_private: Mapped[bool] = mapped_column(default=False)
    is_hidden: Mapped[bool] = mapped_column(default=False)
    open_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    author: Mapped[User] = relationship(lazy="joined")
