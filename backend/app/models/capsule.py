from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, String, ForeignKey, DateTime
from app.database import Base
from app.models.user import User
from app.core.constants import HALL_MAX_LENGTH, TITLE_MAX_LENGTH, CONTENT_MAX_LENGTH
from datetime import datetime

class Capsule(Base):
    __tablename__ = "capsules"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    hall: Mapped[str] = mapped_column(String(HALL_MAX_LENGTH), index=True)
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH))
    content: Mapped[str] = mapped_column(String(CONTENT_MAX_LENGTH))
    is_private: Mapped[bool] = mapped_column(default=False)
    is_hidden: Mapped[bool] = mapped_column(default=False)
    open_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    author: Mapped[User] = relationship(lazy="joined")
