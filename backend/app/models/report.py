from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, ForeignKey, DateTime, String, UniqueConstraint
from app.database import Base
from datetime import datetime

class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (UniqueConstraint("user_id", "capsule_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    capsule_id: Mapped[int] = mapped_column(ForeignKey("capsules.id", ondelete="CASCADE"), index=True)
    reason: Mapped[str | None] = mapped_column(String(200))
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
