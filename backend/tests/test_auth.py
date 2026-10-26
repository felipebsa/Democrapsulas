def test_register_login_and_me(client, make_user):
    headers = make_user("felipe")
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "felipe"


def test_register_duplicate_name(client, make_user):
    make_user("felipe")
    response = client.post("/auth/register", json={"name": "felipe", "password": "123456"})
    assert response.status_code == 409


def test_register_validation(client):
    assert client.post("/auth/register", json={"name": "ab", "password": "123456"}).status_code == 422
    assert client.post("/auth/register", json={"name": "com espaço", "password": "123456"}).status_code == 422
    assert client.post("/auth/register", json={"name": "felipe", "password": "123"}).status_code == 422


def test_login_wrong_password(client, make_user):
    make_user("felipe")
    response = client.post("/auth/login", data={"username": "felipe", "password": "errada"})
    assert response.status_code == 401


def test_me_without_token(client):
    assert client.get("/auth/me").status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer lixo"}).status_code == 401
