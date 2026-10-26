from app.core.config import settings


def test_vote_only_after_open(client, make_user, make_capsule, open_capsule):
    headers = make_user()
    capsule_id = make_capsule(headers)
    assert client.put(f"/capsules/{capsule_id}/vote", json={"value": 1}, headers=headers).status_code == 403

    open_capsule(capsule_id)
    data = client.put(f"/capsules/{capsule_id}/vote", json={"value": 1}, headers=headers).json()
    assert data["score"] == 1
    assert data["my_vote"] == 1


def test_change_and_remove_vote(client, make_user, make_capsule, open_capsule):
    a, b = make_user(), make_user()
    capsule_id = make_capsule(a)
    open_capsule(capsule_id)

    client.put(f"/capsules/{capsule_id}/vote", json={"value": 1}, headers=a)
    client.put(f"/capsules/{capsule_id}/vote", json={"value": 1}, headers=b)
    data = client.put(f"/capsules/{capsule_id}/vote", json={"value": -1}, headers=a).json()
    assert data["score"] == 0
    assert data["my_vote"] == -1

    data = client.delete(f"/capsules/{capsule_id}/vote", headers=a).json()
    assert data["score"] == 1
    assert data["my_vote"] is None


def test_invalid_vote_value(client, make_user, make_capsule, open_capsule):
    headers = make_user()
    capsule_id = make_capsule(headers)
    open_capsule(capsule_id)
    assert client.put(f"/capsules/{capsule_id}/vote", json={"value": 2}, headers=headers).status_code == 422


def test_favorites_gallery(client, make_user, make_capsule, open_capsule):
    headers = make_user()
    first, second = make_capsule(make_user()), make_capsule(make_user())
    open_capsule(first)
    open_capsule(second)

    assert client.put(f"/capsules/{first}/favorite", headers=headers).json()["is_favorite"] is True
    client.put(f"/capsules/{first}/favorite", headers=headers)
    client.put(f"/capsules/{second}/favorite", headers=headers)
    gallery = client.get("/me/favorites", headers=headers).json()
    assert [capsule["id"] for capsule in gallery] == [second, first]

    client.delete(f"/capsules/{first}/favorite", headers=headers)
    assert len(client.get("/me/favorites", headers=headers).json()) == 1


def test_reports_hide_capsule(client, make_user, make_capsule, open_capsule, monkeypatch):
    monkeypatch.setattr(settings, "REPORTS_TO_HIDE", 2)
    owner = make_user()
    capsule_id = make_capsule(owner)
    open_capsule(capsule_id)

    reporter = make_user()
    assert client.post(f"/capsules/{capsule_id}/report", json={"reason": "spam"}, headers=reporter).status_code == 201
    assert client.post(f"/capsules/{capsule_id}/report", json={}, headers=reporter).status_code == 409
    assert client.get(f"/capsules/{capsule_id}").status_code == 200

    client.post(f"/capsules/{capsule_id}/report", json={}, headers=make_user())
    assert client.get(f"/capsules/{capsule_id}").status_code == 404
    assert client.get("/capsules?hall=asiatico").json() == []
    #the owner still sees it
    assert client.get(f"/capsules/{capsule_id}", headers=owner).status_code == 200
