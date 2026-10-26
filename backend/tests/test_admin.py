from app.core.config import settings


def test_admin_only(client, make_user):
    assert client.get("/admin/capsules").status_code == 401
    assert client.get("/admin/capsules", headers=make_user()).status_code == 403
    assert client.get("/admin/capsules", headers=make_user(admin=True)).status_code == 200


def test_review_hidden_capsule(client, make_user, make_capsule, open_capsule, monkeypatch):
    monkeypatch.setattr(settings, "REPORTS_TO_HIDE", 1)
    admin = make_user(admin=True)
    capsule_id = make_capsule(make_user(), content="texto")
    open_capsule(capsule_id)
    client.post(f"/capsules/{capsule_id}/report", json={"reason": "spam"}, headers=make_user())

    hidden = client.get("/admin/capsules?status=hidden", headers=admin).json()
    assert [(capsule["id"], capsule["reports"], capsule["reasons"]) for capsule in hidden] == [(capsule_id, 1, ["spam"])]
    assert hidden[0]["content"] == "texto"

    data = client.post(f"/admin/capsules/{capsule_id}/approve", headers=admin).json()
    assert data["is_hidden"] is False
    assert data["reports"] == 0
    assert client.get(f"/capsules/{capsule_id}").status_code == 200


def test_reported_list_hide_and_delete(client, make_user, make_capsule, open_capsule):
    admin = make_user(admin=True)
    capsule_id = make_capsule(make_user())
    open_capsule(capsule_id)
    client.post(f"/capsules/{capsule_id}/report", json={}, headers=make_user())

    reported = client.get("/admin/capsules?status=reported", headers=admin).json()
    assert [capsule["id"] for capsule in reported] == [capsule_id]

    client.post(f"/admin/capsules/{capsule_id}/hide", headers=admin)
    assert client.get(f"/capsules/{capsule_id}").status_code == 404
    #admins can still open it through the public route
    assert client.get(f"/capsules/{capsule_id}", headers=admin).status_code == 200

    assert client.delete(f"/admin/capsules/{capsule_id}", headers=admin).status_code == 204
    assert client.delete(f"/admin/capsules/{capsule_id}", headers=admin).status_code == 404
