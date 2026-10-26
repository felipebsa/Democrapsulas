from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, ForeignKey, DateTime, UniqueConstraint
from app.database import Base
from datetime import datetime

class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "capsule_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    capsule_id: Mapped[int] = mapped_column(ForeignKey("capsules.id", ondelete="CASCADE"), index=True)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
