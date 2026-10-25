from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, String, ForeignKey, DateTime
from app.database import Base
from datetime import datetime

class Capsule(Base):
    __tablename__ = "capsules"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    is_private: Mapped[bool] = mapped_column(default=False)
    is_hidden: Mapped[bool] = mapped_column(default=False)
    open_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
