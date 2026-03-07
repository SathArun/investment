from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from jose import jwt
from unittest.mock import patch

from app.main import app
from app.db.base import Base, get_db
from app.config import settings
from app.auth.models import Advisor
from app.goals.models import Client


def make_token(advisor_id: str) -> str:
    return jwt.encode({"sub": advisor_id}, settings.JWT_SECRET_KEY, algorithm="HS256")


@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Import all models so metadata is fully populated
    import app.auth.models  # noqa: F401
    import app.market_data.models  # noqa: F401
    import app.analytics.models  # noqa: F401
    import app.goals.models  # noqa: F401
    import app.risk_profiler.models  # noqa: F401
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


def seed_advisor(session, advisor_id: str = "advisor_1"):
    """Insert an Advisor row to satisfy FK constraint."""
    advisor = Advisor(
        id=advisor_id,
        email=f"{advisor_id}@example.com",
        password_hash="hashed",
        name=f"Advisor {advisor_id}",
    )
    session.add(advisor)
    session.commit()
    return advisor


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_create_client_returns_201(client):
    test_client, session = client
    seed_advisor(session, "advisor_1")
    token = make_token("advisor_1")
    response = test_client.post(
        "/api/clients",
        json={"name": "Ramesh Kumar", "age": 35, "tax_bracket": 0.30, "risk_category": "Moderate"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ramesh Kumar"
    assert data["age"] == 35
    assert data["tax_bracket"] == 0.30
    assert data["risk_category"] == "Moderate"
    assert data["advisor_id"] == "advisor_1"
    assert "id" in data
    assert "created_at" in data


def test_list_clients_scoped_to_advisor(client):
    test_client, session = client
    seed_advisor(session, "advisor_1")
    seed_advisor(session, "advisor_2")

    token1 = make_token("advisor_1")
    token2 = make_token("advisor_2")

    # Create 2 clients for advisor_1
    for name in ["Client A", "Client B"]:
        test_client.post(
            "/api/clients",
            json={"name": name},
            headers={"Authorization": f"Bearer {token1}"},
        )

    # Create 1 client for advisor_2
    test_client.post(
        "/api/clients",
        json={"name": "Client C"},
        headers={"Authorization": f"Bearer {token2}"},
    )

    # advisor_1 should see only their 2 clients
    resp1 = test_client.get("/api/clients", headers={"Authorization": f"Bearer {token1}"})
    assert resp1.status_code == 200
    assert len(resp1.json()) == 2

    # advisor_2 should see only their 1 client
    resp2 = test_client.get("/api/clients", headers={"Authorization": f"Bearer {token2}"})
    assert resp2.status_code == 200
    assert len(resp2.json()) == 1


def test_get_client_returns_correct_data(client):
    test_client, session = client
    seed_advisor(session, "advisor_1")
    token = make_token("advisor_1")

    create_resp = test_client.post(
        "/api/clients",
        json={"name": "Priya Sharma", "age": 42, "tax_bracket": 0.20, "risk_category": "Conservative"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client_id = create_resp.json()["id"]

    get_resp = test_client.get(
        f"/api/clients/{client_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == client_id
    assert data["name"] == "Priya Sharma"
    assert data["age"] == 42
    assert data["tax_bracket"] == 0.20
    assert data["risk_category"] == "Conservative"


def test_get_other_advisors_client_returns_404(client):
    """No information disclosure — cross-advisor access returns 404, not 403."""
    test_client, session = client
    seed_advisor(session, "advisor_1")
    seed_advisor(session, "advisor_2")

    token1 = make_token("advisor_1")
    token2 = make_token("advisor_2")

    # advisor_1 creates a client
    create_resp = test_client.post(
        "/api/clients",
        json={"name": "Secret Client"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    client_id = create_resp.json()["id"]

    # advisor_2 tries to access advisor_1's client — must get 404
    resp = test_client.get(
        f"/api/clients/{client_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert resp.status_code == 404


def test_patch_client_updates_fields(client):
    test_client, session = client
    seed_advisor(session, "advisor_1")
    token = make_token("advisor_1")

    create_resp = test_client.post(
        "/api/clients",
        json={"name": "Suresh Patel", "age": 50},
        headers={"Authorization": f"Bearer {token}"},
    )
    client_id = create_resp.json()["id"]

    patch_resp = test_client.patch(
        f"/api/clients/{client_id}",
        json={"age": 51, "tax_bracket": 0.10, "risk_category": "Aggressive"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["age"] == 51
    assert data["tax_bracket"] == 0.10
    assert data["risk_category"] == "Aggressive"
    assert data["name"] == "Suresh Patel"  # unchanged
    assert data["updated_at"] is not None


def test_create_client_invalid_tax_bracket_returns_422(client):
    test_client, session = client
    seed_advisor(session, "advisor_1")
    token = make_token("advisor_1")

    resp = test_client.post(
        "/api/clients",
        json={"name": "Invalid Tax Client", "tax_bracket": 0.99},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


def test_create_20_clients_all_returned(client):
    test_client, session = client
    seed_advisor(session, "advisor_1")
    token = make_token("advisor_1")

    for i in range(20):
        resp = test_client.post(
            "/api/clients",
            json={"name": f"Client {i:02d}"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201

    list_resp = test_client.get("/api/clients", headers={"Authorization": f"Bearer {token}"})
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 20
