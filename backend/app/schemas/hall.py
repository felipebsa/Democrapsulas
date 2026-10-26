from datetime import datetime
from pydantic import BaseModel

class SchemaSong(BaseModel):
    id: int
    hall: str
    title: str
    file: str
    votes: int


#candidates of the current week
class SchemaSongVoting(BaseModel):
    hall: str
    week_start: datetime
    week_end: datetime
    my_vote: int | None
    songs: list[SchemaSong]


class SchemaSongVote(BaseModel):
    song_id: int


class SchemaTrack(BaseModel):
    hall: str
    song: SchemaSong | None
    #week whose voting chose the song (None when nobody has voted yet)
    week_start: datetime | None


class SchemaSeason(BaseModel):
    season: str
    started_at: datetime
    ends_at: datetime
    seconds_left: float
    server_time: datetime
