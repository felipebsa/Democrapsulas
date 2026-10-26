from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, String, ForeignKey, DateTime, Index
from app.database import Base
from app.core.constants import HALL_MAX_LENGTH
from datetime import datetime

#candidate songs of each hall
class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(primary_key=True)
    hall: Mapped[str] = mapped_column(String(HALL_MAX_LENGTH), index=True)
    title: Mapped[str] = mapped_column(String(100))
    file: Mapped[str] = mapped_column(String(200))
    position: Mapped[int] = mapped_column(default=0)


#every vote (or vote change) is a new row, so the tie rule can replay the week in order
class SongVote(Base):
    __tablename__ = "song_votes"
    __table_args__ = (Index("ix_song_votes_hall_week", "hall", "week_start"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"))
    hall: Mapped[str] = mapped_column(String(HALL_MAX_LENGTH))
    week_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
