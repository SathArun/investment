from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.main import app
from app.db.base import Base, get_db
from app.auth.service import create_advisor, create_access_token
from app.auth.router import router as auth_router


# Register auth router on the app if not already registered
_auth_routes = {r.path for r in app.routes}
if "/api/auth/login" not in _auth_routes:
    app.include_router(auth_router)


@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session, engine
    session.close()
    engine.dispose()


@pytest.fixture(autouse=True)
def no_scheduler():
    with patch("app.jobs.scheduler.start", lambda: None), \
         patch("app.jobs.scheduler.stop", lambda: None):
        yield


@pytest.fixture
def client(test_db):
    session, engine = test_db
    Session = sessionmaker(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app), session
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_login_valid_credentials_returns_tokens(client):
    test_client, session = client
    create_advisor(session, email="a@test.com", password="pass123!", name="Test")

    response = test_client.post("/api/auth/login", json={
        "email": "a@test.com",
        "password": "pass123!",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["advisor"]["email"] == "a@test.com"


def test_login_invalid_password_returns_401(client):
    test_client, session = client
    create_advisor(session, email="a@test.com", password="pass123!", name="Test")

    response = test_client.post("/api/auth/login", json={
        "email": "a@test.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_login_unknown_email_returns_401(client):
    test_client, session = client

    response = test_client.post("/api/auth/login", json={
        "email": "nobody@nowhere.com",
        "password": "pass123!",
    })
    assert response.status_code == 401


def test_refresh_token_rotates_successfully(client):
    test_client, session = client
    create_advisor(session, email="a@test.com", password="pass123!", name="Test")

    # Login to get tokens
    login_resp = test_client.post("/api/auth/login", json={
        "email": "a@test.com",
        "password": "pass123!",
    })
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]

    # Rotate the refresh token
    refresh_resp = test_client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # New refresh token should differ from the old one
    assert data["refresh_token"] != refresh_token


def test_refresh_token_used_twice_returns_401(client):
    test_client, session = client
    create_advisor(session, email="a@test.com", password="pass123!", name="Test")

    # Login to get tokens
    login_resp = test_client.post("/api/auth/login", json={
        "email": "a@test.com",
        "password": "pass123!",
    })
    refresh_token = login_resp.json()["refresh_token"]

    # First use: should succeed
    first_resp = test_client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert first_resp.status_code == 200

    # Second use of the same (now revoked) token: should fail
    second_resp = test_client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert second_resp.status_code == 401


def test_protected_endpoint_no_token_returns_403(client):
    test_client, session = client
    # /api/products requires auth; no token provided -> 403 from HTTPBearer
    response = test_client.get("/api/products?tax_bracket=0.30&time_horizon=long")
    assert response.status_code == 403


def test_protected_endpoint_valid_token_returns_200(client):
    test_client, session = client
    advisor = create_advisor(session, email="a@test.com", password="pass123!", name="Test")
    access_token = create_access_token(advisor.id)

    response = test_client.get(
        "/api/products?tax_bracket=0.30&time_horizon=long",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    # 200 means auth passed (no products seeded but endpoint returns empty list, not 401)
    assert response.status_code == 200


def test_expired_refresh_token_returns_401(client):
    """A refresh token past its expires_at must be rejected with 401."""
    from datetime import datetime, timedelta
    from app.auth.models import RefreshToken

    test_client, session = client
    create_advisor(session, email="b@test.com", password="pass123!", name="Test")

    login_resp = test_client.post("/api/auth/login", json={
        "email": "b@test.com", "password": "pass123!",
    })
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]

    # Manually expire the token in the DB
    token_id = refresh_token.split(".")[0]
    record = session.get(RefreshToken, token_id)
    record.expires_at = datetime.utcnow() - timedelta(days=1)
    session.commit()

    resp = test_client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 401


def test_malformed_refresh_token_returns_401(client):
    """A refresh token with no dot separator must be rejected with 401."""
    test_client, _ = client
    resp = test_client.post("/api/auth/refresh", json={"refresh_token": "nodotinhere"})
    assert resp.status_code == 401
