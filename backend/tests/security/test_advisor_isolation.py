"""Security tests: cross-advisor data isolation (Advisor B cannot access Advisor A's data)."""
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


CONSERVATIVE_ANSWERS = [
    {"question_id": "q01", "selected_value": "above_60"},
    {"question_id": "q02", "selected_value": "retire_below_50"},
    {"question_id": "q03", "selected_value": "irregular"},
    {"question_id": "q04", "selected_value": "below_5L"},
    {"question_id": "q05", "selected_value": "five_plus"},
    {"question_id": "q06", "selected_value": "below_10pct"},
    {"question_id": "q07", "selected_value": "no"},
    {"question_id": "q08", "selected_value": "capital_preservation"},
    {"question_id": "q09", "selected_value": "below_6pct"},
    {"question_id": "q10", "selected_value": "no_loss"},
    {"question_id": "q11", "selected_value": "below_3yr"},
    {"question_id": "q12", "selected_value": "likely"},
    {"question_id": "q13", "selected_value": "no_goal"},
    {"question_id": "q14", "selected_value": "sell_all"},
    {"question_id": "q15", "selected_value": "none"},
    {"question_id": "q16", "selected_value": "low_gain_no_loss"},
    {"question_id": "q17", "selected_value": "large"},
    {"question_id": "q18", "selected_value": "below_3"},
]


@pytest.fixture(autouse=True)
def no_scheduler():
    with patch("app.jobs.scheduler.start", lambda: None), \
         patch("app.jobs.scheduler.stop", lambda: None):
        yield


def _make_advisor(session_factory, email: str, password: str, name: str) -> str:
    """Create an advisor and return the advisor_id (captured before session close)."""
    db = session_factory()
    advisor = create_advisor(db, email=email, password=password, name=name)
    advisor_id = str(advisor.id)  # capture before close to avoid DetachedInstanceError
    db.close()
    return advisor_id


@pytest.fixture
def isolation_setup():
    """Create in-memory DB, two advisors, and a TestClient."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Seed reference data
    from app.db.seed import seed_asset_classes, seed_tax_rules
    db = Session()
    seed_asset_classes(db)
    seed_tax_rules(db)
    db.commit()
    db.close()

    # Create Advisor A and Advisor B — capture IDs before session close
    advisor_a_id = _make_advisor(Session, "advisor_a@test.com", "PasswordA123!", "Advisor A")
    advisor_b_id = _make_advisor(Session, "advisor_b@test.com", "PasswordB123!", "Advisor B")

    token_a = create_access_token(advisor_a_id)
    token_b = create_access_token(advisor_b_id)

    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client, token_a, token_b
    app.dependency_overrides.clear()
    engine.dispose()


def _create_client_for_advisor(test_client, token: str, name: str = "Client A") -> str:
    """Helper: create a client and return client_id."""
    r = test_client.post(
        "/api/clients",
        json={"name": name, "age": 40, "tax_bracket": 0.30},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201, f"Client creation failed: {r.text}"
    return r.json()["id"]


def _create_goal_for_advisor(test_client, token: str, client_id: str) -> str:
    """Helper: create a goal and return goal_id."""
    r = test_client.post(
        "/api/goals",
        json={
            "client_id": client_id,
            "name": "Retirement Goal",
            "target_amount_inr": 5000000.0,
            "current_corpus_inr": 100000.0,
            "monthly_sip_inr": 10000.0,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201, f"Goal creation failed: {r.text}"
    return r.json()["id"]


def _create_risk_profile_for_advisor(test_client, token: str, client_id: str) -> str:
    """Helper: create a risk profile and return risk_profile_id."""
    r = test_client.post(
        "/api/risk-profiles",
        json={
            "client_id": client_id,
            "responses": CONSERVATIVE_ANSWERS,
            "advisor_rationale": "Test isolation rationale for compliance.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201, f"Risk profile creation failed: {r.text}"
    return r.json()["id"]


class TestAdvisorIsolation:
    """Verify that Advisor B cannot access any resources belonging to Advisor A."""

    def test_get_clients_isolation(self, isolation_setup):
        """Advisor B's client list must not include Advisor A's clients."""
        test_client, token_a, token_b = isolation_setup

        # Advisor A creates a client
        _create_client_for_advisor(test_client, token_a, name="Advisor A Client")

        # Advisor B lists clients — should see zero clients
        r = test_client.get(
            "/api/clients",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r.status_code == 200
        clients_b = r.json()
        if isinstance(clients_b, dict):
            clients_b = clients_b.get("clients", [])
        assert len(clients_b) == 0, (
            f"Advisor B should see 0 clients but got {len(clients_b)}: {clients_b}"
        )

    def test_get_client_by_id_returns_404(self, isolation_setup):
        """Advisor B gets 404 (not 403) when accessing Advisor A's client by ID."""
        test_client, token_a, token_b = isolation_setup

        # Advisor A creates a client
        client_id = _create_client_for_advisor(test_client, token_a, name="Advisor A Client")

        # Advisor B tries to access by ID
        r = test_client.get(
            f"/api/clients/{client_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r.status_code == 404, (
            f"Expected 404 for cross-advisor client access, got {r.status_code}: {r.text}"
        )

    def test_goal_plan_isolation(self, isolation_setup):
        """Advisor B gets 404 when accessing Advisor A's goal plan."""
        test_client, token_a, token_b = isolation_setup

        # Advisor A creates client and goal
        client_id = _create_client_for_advisor(test_client, token_a)
        goal_id = _create_goal_for_advisor(test_client, token_a, client_id)

        # Advisor B tries to access the goal plan
        r = test_client.get(
            f"/api/goals/{goal_id}/plan",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r.status_code == 404, (
            f"Expected 404 for cross-advisor goal plan access, got {r.status_code}: {r.text}"
        )

    def test_pdf_client_report_isolation(self, isolation_setup):
        """Advisor B gets 404 when generating a PDF report for Advisor A's client."""
        test_client, token_a, token_b = isolation_setup

        # Advisor A creates a client
        client_id = _create_client_for_advisor(test_client, token_a)

        # Advisor B tries to generate a report for that client
        r = test_client.post(
            "/api/pdf/client-report",
            json={
                "client_id": client_id,
                "product_ids": ["some_product"],
                "tax_bracket": 0.30,
                "time_horizon": "long",
            },
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r.status_code == 404, (
            f"Expected 404 for cross-advisor PDF report, got {r.status_code}: {r.text}"
        )

    def test_risk_profile_isolation(self, isolation_setup):
        """Advisor B gets 404 when generating a compliance pack for Advisor A's risk profile."""
        test_client, token_a, token_b = isolation_setup

        # Advisor A creates client and risk profile
        client_id = _create_client_for_advisor(test_client, token_a)
        risk_profile_id = _create_risk_profile_for_advisor(test_client, token_a, client_id)

        # Advisor B tries to generate a compliance pack for that risk profile
        r = test_client.post(
            "/api/pdf/compliance-pack",
            json={"risk_profile_id": risk_profile_id},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r.status_code == 404, (
            f"Expected 404 for cross-advisor compliance pack, got {r.status_code}: {r.text}"
        )
