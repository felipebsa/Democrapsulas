from datetime import datetime, time, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.song import Song, SongVote

#Brasília time (no daylight saving since 2019)
BRT = timezone(timedelta(hours=-3))


def get_week_start(moment: datetime) -> datetime:
    local = moment.astimezone(BRT)
    monday = local.date() - timedelta(days=local.weekday())
    return datetime.combine(monday, time(0), tzinfo=BRT)


def get_songs(db: Session, hall: str) -> list[Song]:
    query = select(Song).where(Song.hall == hall).order_by(Song.position, Song.id)
    return db.execute(query).scalars().all()


def tally_week(db: Session, hall: str, week_start: datetime):
    """Replays the week's votes in order.

    Returns (counts, current_votes, winner_id): counts per song, the current
    song of each user and the winner (most votes; on a tie, the song that
    reached that number of votes first). winner_id is None without votes.
    """
    query = (
        select(SongVote)
        .where(SongVote.hall == hall, SongVote.week_start == week_start)
        .order_by(SongVote.id)
    )
    counts: dict[int, int] = {}
    current_votes: dict[int, int] = {}
    reached_at: dict[tuple[int, int], int] = {}

    for step, vote in enumerate(db.execute(query).scalars()):
        previous = current_votes.get(vote.user_id)
        if previous == vote.song_id:
            continue
        if previous is not None:
            counts[previous] -= 1
        current_votes[vote.user_id] = vote.song_id
        counts[vote.song_id] = counts.get(vote.song_id, 0) + 1
        reached_at.setdefault((vote.song_id, counts[vote.song_id]), step)

    best = max(counts.values(), default=0)
    if best == 0:
        return counts, current_votes, None

    tied = [song_id for song_id, total in counts.items() if total == best]
    winner_id = min(tied, key=lambda song_id: reached_at[(song_id, best)])
    return counts, current_votes, winner_id


def get_track(db: Session, hall: str, now: datetime):
    """Song the hall plays now: winner of the last finished week with votes.

    Returns (song, week_start, votes). Falls back to the first candidate.
    """
    current_week = get_week_start(now)
    weeks_query = (
        select(SongVote.week_start)
        .where(SongVote.hall == hall, SongVote.week_start < current_week)
        .distinct()
        .order_by(SongVote.week_start.desc())
    )
    for week_start in db.execute(weeks_query).scalars():
        counts, _, winner_id = tally_week(db, hall, week_start)
        if winner_id is not None:
            return db.get(Song, winner_id), week_start, counts[winner_id]

    songs = get_songs(db, hall)
    return (songs[0] if songs else None), None, 0
