def test_random_capsule(client, make_user, make_capsule, open_capsule):
    headers = make_user()
    assert client.get("/capsules/random").status_code == 404

    make_capsule(headers, hall="espaco")
    assert client.get("/capsules/random").status_code == 404

    opened = make_capsule(headers, hall="espaco")
    open_capsule(opened)
    private = make_capsule(headers, hall="espaco", is_private=True)
    open_capsule(private)

    for _ in range(5):
        assert client.get("/capsules/random").json()["id"] == opened
    assert client.get("/capsules/random?hall=medieval").status_code == 404


def test_ranking(client, make_user, make_capsule, open_capsule):
    a, b = make_user(), make_user()
    first, second, negative, closed = (make_capsule(a) for _ in range(4))
    for capsule_id in (first, second, negative):
        open_capsule(capsule_id)

    client.put(f"/capsules/{first}/vote", json={"value": 1}, headers=a)
    client.put(f"/capsules/{second}/vote", json={"value": 1}, headers=a)
    client.put(f"/capsules/{second}/vote", json={"value": 1}, headers=b)
    client.put(f"/capsules/{negative}/vote", json={"value": -1}, headers=a)

    ranking = client.get("/ranking").json()
    assert [(capsule["id"], capsule["score"]) for capsule in ranking] == [(second, 2), (first, 1)]
    assert len(client.get("/ranking?limit=1").json()) == 1
    assert client.get("/ranking?hall=medieval").json() == []


def test_stats(client, make_user, make_capsule, open_capsule):
    headers = make_user()
    opened = make_capsule(headers, hall="cyberpunk")
    open_capsule(opened)
    make_capsule(headers, hall="cyberpunk")
    make_capsule(headers, hall="medieval", is_private=True)
    client.put(f"/capsules/{opened}/vote", json={"value": 1}, headers=headers)

    data = client.get("/stats").json()
    assert data["users"] == 1
    assert data["capsules"] == 3
    assert data["open_capsules"] == 1
    assert data["waiting_capsules"] == 2
    assert data["private_capsules"] == 1
    assert data["capsules_per_hall"]["cyberpunk"] == 2
    assert data["capsules_per_hall"]["medieval"] == 0
    assert data["votes"] == 1
