from datetime import datetime, timedelta, timezone
from app.core.config import settings
from tests.conftest import future


def test_create_capsule(client, make_user):
    headers = make_user()
    body = {"hall": "medieval", "title": "Oi", "lantern": 3, "content": "Mensagem", "open_at": future()}
    response = client.post("/capsules", json=body, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["hall"] == "medieval"
    assert data["lantern"] == 3
    assert data["is_mine"] is True
    assert data["is_open"] is False
    #the owner can read their own capsule
    assert data["content"] == "Mensagem"


def test_create_capsule_needs_login(client):
    body = {"hall": "medieval", "title": "Oi", "lantern": 3, "content": "Mensagem", "open_at": future()}
    assert client.post("/capsules", json=body).status_code == 401


def test_create_capsule_validation(client, make_user):
    headers = make_user()
    base = {"hall": "medieval", "title": "Oi", "lantern": 3, "content": "Mensagem", "open_at": future()}
    past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()

    assert client.post("/capsules", json={**base, "hall": "praia"}, headers=headers).status_code == 422
    assert client.post("/capsules", json={**base, "open_at": past}, headers=headers).status_code == 422
    assert client.post("/capsules", json={**base, "open_at": "2030-01-01T00:00:00"}, headers=headers).status_code == 422
    assert client.post("/capsules", json={**base, "content": "x" * 1001}, headers=headers).status_code == 422
    assert client.post("/capsules", json={**base, "title": "   "}, headers=headers).status_code == 422
    assert client.post("/capsules", json={**base, "lantern": 0}, headers=headers).status_code == 422
    assert client.post("/capsules", json={**base, "lantern": 18}, headers=headers).status_code == 422


def test_create_capsule_bad_words(client, make_user):
    headers = make_user()
    body = {"hall": "medieval", "title": "Oi", "lantern": 3, "content": "que M3RRRDA", "open_at": future()}
    assert client.post("/capsules", json=body, headers=headers).status_code == 422


def test_cooldown(client, make_user, make_capsule, monkeypatch):
    monkeypatch.setattr(settings, "CAPSULE_COOLDOWN_SECONDS", 60)
    headers = make_user()
    make_capsule(headers)
    body = {"hall": "medieval", "title": "Oi", "lantern": 3, "content": "Mensagem", "open_at": future()}
    response = client.post("/capsules", json=body, headers=headers)
    assert response.status_code == 429


def test_daily_limit(client, make_user, make_capsule, monkeypatch):
    monkeypatch.setattr(settings, "CAPSULES_PER_DAY", 2)
    headers = make_user()
    make_capsule(headers)
    make_capsule(headers)
    body = {"hall": "medieval", "title": "Oi", "lantern": 3, "content": "Mensagem", "open_at": future()}
    assert client.post("/capsules", json=body, headers=headers).status_code == 429


def test_content_hidden_until_open(client, make_user, make_capsule, open_capsule):
    capsule_id = make_capsule(make_user(), content="segredo")
    viewer = make_user()

    data = client.get(f"/capsules/{capsule_id}", headers=viewer).json()
    assert data["is_open"] is False
    assert data["content"] is None
    assert data["title"] is None
    assert data["author"] is None

    open_capsule(capsule_id)
    data = client.get(f"/capsules/{capsule_id}").json()
    assert data["is_open"] is True
    assert data["content"] == "segredo"
    assert data["author"] is not None


def test_private_capsule_only_for_owner(client, make_user, make_capsule):
    owner = make_user()
    capsule_id = make_capsule(owner, is_private=True)
    assert client.get(f"/capsules/{capsule_id}").status_code == 404
    assert client.get(f"/capsules/{capsule_id}", headers=make_user()).status_code == 404
    assert client.get(f"/capsules/{capsule_id}", headers=owner).status_code == 200


def test_list_hall(client, make_user, make_capsule, monkeypatch):
    headers = make_user()
    make_capsule(headers, hall="espaco")
    make_capsule(headers, hall="espaco")
    make_capsule(headers, hall="espaco", is_private=True)
    make_capsule(headers, hall="medieval")

    assert len(client.get("/capsules?hall=espaco").json()) == 2
    assert client.get("/capsules?hall=praia").status_code == 422

    monkeypatch.setattr(settings, "HALL_CAPSULE_LIMIT", 1)
    assert len(client.get("/capsules?hall=espaco").json()) == 1


def test_my_capsules(client, make_user, make_capsule):
    headers = make_user()
    make_capsule(headers)
    make_capsule(headers, is_private=True)
    make_capsule(make_user())
    assert len(client.get("/me/capsules", headers=headers).json()) == 2


def test_delete_capsule(client, make_user, make_capsule):
    owner = make_user()
    capsule_id = make_capsule(owner)
    assert client.delete(f"/capsules/{capsule_id}", headers=make_user()).status_code == 404
    assert client.delete(f"/capsules/{capsule_id}", headers=owner).status_code == 204
    assert client.get(f"/capsules/{capsule_id}").status_code == 404


def test_invalid_token_on_public_route_is_anonymous(client, make_user, make_capsule):
    capsule_id = make_capsule(make_user())
    response = client.get(f"/capsules/{capsule_id}", headers={"Authorization": "Bearer vencido"})
    assert response.status_code == 200
    assert response.json()["is_mine"] is False
