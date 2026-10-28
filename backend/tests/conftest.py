import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

#tests use their own database: <DATABASE_URL name>_test (or TEST_DATABASE_URL)
#this must run before importing the app, so the engine points to it
from app.core.config import settings

test_url = os.environ.get("TEST_DATABASE_URL") or str(
    make_url(settings.DATABASE_URL).set(database=make_url(settings.DATABASE_URL).database + "_test")
    .render_as_string(hide_password=False)
)
os.environ["DATABASE_URL"] = test_url
settings.DATABASE_URL = test_url

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from app.database import SessionLocal, engine
from app.main import app
from app.models.capsule import Capsule

TABLES = "users, capsules, votes, favorites, reports, song_votes"


def create_test_database():
    url = make_url(test_url)
    admin_engine = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(text("select 1 from pg_database where datname = :name"), {"name": url.database}).scalar()
        if not exists:
            conn.execute(text(f'create database "{url.database}"'))
    admin_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def database():
    create_test_database()
    config = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    config.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "..", "alembic"))
    command.upgrade(config, "head")
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_tables(monkeypatch):
    #most tests create several capsules in a row
    monkeypatch.setattr(settings, "CAPSULE_COOLDOWN_SECONDS", 0)
    yield
    with engine.begin() as conn:
        conn.execute(text(f"truncate {TABLES} restart identity cascade"))


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def make_user(client, db):
    def make(name: str | None = None, admin: bool = False) -> dict:
        name = name or "u_" + uuid.uuid4().hex[:8]
        assert client.post("/auth/register", json={"name": name, "password": "123456"}).status_code == 201
        if admin:
            db.execute(text("update users set is_admin = true where name = :name"), {"name": name})
            db.commit()
        token = client.post("/auth/login", data={"username": name, "password": "123456"}).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return make


def future(days: int = 1) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


@pytest.fixture
def make_capsule(client):
    def make(headers: dict, hall: str = "asiatico", title: str = "titulo", content: str = "mensagem", is_private: bool = False) -> int:
        body = {"hall": hall, "title": title, "content": content, "lantern": 1, "is_private": is_private, "open_at": future()}
        response = client.post("/capsules", json=body, headers=headers)
        assert response.status_code == 201, response.text
        return response.json()["id"]
    return make


#moves open_at to the past, as if the time had passed
@pytest.fixture
def open_capsule(db):
    def make_open(capsule_id: int):
        capsule = db.get(Capsule, capsule_id)
        capsule.open_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    return make_open
