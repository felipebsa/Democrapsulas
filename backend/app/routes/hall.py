from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.song import Song, SongVote
from app.core.constants import HALLS, HALL_NAMES, Hall, SEASONS, SEASON_SECONDS
from app.core.security import get_current_user, get_optional_user
from app.schemas.hall import SchemaHall, SchemaSong, SchemaSongVoting, SchemaSongVote, SchemaTrack, SchemaSeason
from app.core.clock import now_utc
from app.services.music import get_week_start, get_songs, tally_week, get_track

router = APIRouter(prefix="/halls", tags=["halls"])

def build_voting(db: Session, hall: str, c_user) -> SchemaSongVoting:
    week_start = get_week_start(now_utc())
    counts, current_votes, _ = tally_week(db, hall, week_start)
    songs = [
        SchemaSong(id=song.id, hall=song.hall, title=song.title, file=song.file, votes=counts.get(song.id, 0))
        for song in get_songs(db, hall)
    ]
    return SchemaSongVoting(
        hall=hall,
        week_start=week_start,
        week_end=week_start + timedelta(days=7),
        my_vote=current_votes.get(c_user.id) if c_user else None,
        songs=songs,
    )

@router.get("", response_model=list[SchemaHall])
def list_halls():
    return [SchemaHall(id=hall, name=HALL_NAMES[hall]) for hall in HALLS]

#current season of the seasons hall, from the server clock so everyone sees the same
@router.get("/estacoes/season", response_model=SchemaSeason)
def current_season():
    now = now_utc()
    cycle = int(now.timestamp() // SEASON_SECONDS)
    started_at = datetime.fromtimestamp(cycle * SEASON_SECONDS, timezone.utc)
    ends_at = started_at + timedelta(seconds=SEASON_SECONDS)
    return SchemaSeason(
        season=SEASONS[cycle % len(SEASONS)],
        started_at=started_at,
        ends_at=ends_at,
        seconds_left=(ends_at - now).total_seconds(),
        server_time=now,
    )

@router.get("/{hall}/songs", response_model=SchemaSongVoting)
def song_voting(hall: Hall, db: Session = Depends(get_db), c_user=Depends(get_optional_user)):
    return build_voting(db, hall, c_user)

@router.put("/{hall}/songs/vote", response_model=SchemaSongVoting)
def vote_song(hall: Hall, vote: SchemaSongVote, db: Session = Depends(get_db), c_user=Depends(get_current_user)):
    song = db.get(Song, vote.song_id)
    if not song or song.hall != hall:
        raise HTTPException(status_code=404, detail="Song not found in this hall")

    week_start = get_week_start(now_utc())
    _, current_votes, _ = tally_week(db, hall, week_start)
    if current_votes.get(c_user.id) != song.id:
        db.add(SongVote(user_id=c_user.id, song_id=song.id, hall=hall, week_start=week_start))
        db.commit()
    return build_voting(db, hall, c_user)

#song the hall plays this week: winner of last week's voting
@router.get("/{hall}/track", response_model=SchemaTrack)
def hall_track(hall: Hall, db: Session = Depends(get_db)):
    song, week_start, votes = get_track(db, hall, now_utc())
    if not song:
        return SchemaTrack(hall=hall, song=None, week_start=None)

    return SchemaTrack(
        hall=hall,
        song=SchemaSong(id=song.id, hall=song.hall, title=song.title, file=song.file, votes=votes),
        week_start=week_start,
    )
