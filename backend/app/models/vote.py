from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, ForeignKey, DateTime, SmallInteger, UniqueConstraint
from app.database import Base
from datetime import datetime

#one vote per user per capsule: +1 or -1
class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("user_id", "capsule_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    capsule_id: Mapped[int] = mapped_column(ForeignKey("capsules.id", ondelete="CASCADE"), index=True)
    value: Mapped[int] = mapped_column(SmallInteger)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
