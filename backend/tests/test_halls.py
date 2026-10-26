from datetime import datetime, timedelta
from sqlalchemy import update
from app.models.song import SongVote
from app.services.music import BRT, get_week_start


def song_ids(client, hall="medieval"):
    return [song["id"] for song in client.get(f"/halls/{hall}/songs").json()["songs"]]


def vote(client, headers, song_id, hall="medieval"):
    return client.put(f"/halls/{hall}/songs/vote", json={"song_id": song_id}, headers=headers)


def finish_week(db):
    db.execute(update(SongVote).values(week_start=SongVote.week_start - timedelta(days=7)))
    db.commit()


def test_each_hall_has_three_songs(client):
    for hall in ("asiatico", "medieval", "cyberpunk", "espaco", "estacoes"):
        assert len(song_ids(client, hall)) == 3


def test_week_start_brasilia():
    sunday_night = datetime(2026, 11, 1, 23, 59, tzinfo=BRT)
    monday = datetime(2026, 11, 2, 0, 0, tzinfo=BRT)
    assert get_week_start(sunday_night) == datetime(2026, 10, 26, tzinfo=BRT)
    assert get_week_start(monday) == monday


def test_vote_and_change_vote(client, make_user):
    headers = make_user()
    first, second, _ = song_ids(client)

    data = vote(client, headers, first).json()
    assert data["my_vote"] == first
    data = vote(client, headers, second).json()
    votes = {song["id"]: song["votes"] for song in data["songs"]}
    assert votes[first] == 0
    assert votes[second] == 1
    assert data["my_vote"] == second


def test_vote_song_from_other_hall(client, make_user):
    other_hall_song = song_ids(client, "espaco")[0]
    assert vote(client, make_user(), other_hall_song).status_code == 404


def test_track_without_votes_is_first_song(client):
    data = client.get("/halls/medieval/track").json()
    assert data["song"]["id"] == song_ids(client)[0]
    assert data["week_start"] is None


def test_track_ignores_current_week(client, make_user):
    vote(client, make_user(), song_ids(client)[2])
    assert client.get("/halls/medieval/track").json()["song"]["id"] == song_ids(client)[0]


def test_track_winner_of_last_week(client, make_user, db):
    first, second, third = song_ids(client)
    for _ in range(2):
        vote(client, make_user(), third)
    vote(client, make_user(), second)
    finish_week(db)

    data = client.get("/halls/medieval/track").json()
    assert data["song"]["id"] == third
    assert data["song"]["votes"] == 2


def test_track_tie_first_to_reach_top_score(client, make_user, db):
    first, second, _ = song_ids(client)
    a, b, c, d = (make_user() for _ in range(4))
    vote(client, a, first)
    vote(client, b, second)
    vote(client, c, second)  # second reaches 2 votes here
    vote(client, d, first)   # first reaches 2 votes later
    finish_week(db)
    assert client.get("/halls/medieval/track").json()["song"]["id"] == second


def test_track_tie_counts_vote_changes(client, make_user, db):
    first, second, _ = song_ids(client)
    a, b, c, d = (make_user() for _ in range(4))
    vote(client, a, first)
    vote(client, b, first)   # first reaches 2
    vote(client, b, second)  # b changes: first drops to 1
    vote(client, c, second)  # second reaches 2
    vote(client, d, first)   # first back to 2
    finish_week(db)
    #both end with 2: first got there before second, even after dropping
    assert client.get("/halls/medieval/track").json()["song"]["id"] == first


def test_track_keeps_last_winner_after_empty_week(client, make_user, db):
    third = song_ids(client)[2]
    vote(client, make_user(), third)
    finish_week(db)
    finish_week(db)
    assert client.get("/halls/medieval/track").json()["song"]["id"] == third


def test_season(client):
    data = client.get("/halls/estacoes/season").json()
    assert data["season"] in ("primavera", "verao", "outono", "inverno")
    assert 0 < data["seconds_left"] <= 120
