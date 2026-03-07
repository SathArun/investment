"""E2E test: full advisor workflow exercising all major API endpoints."""
from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.main import app
from app.db.base import Base, get_db
from app.auth.service import create_advisor, create_access_token


# ---------------------------------------------------------------------------
# Conservative answer map for the 18 SEBI risk questionnaire questions
# (each selects the lowest-scoring option → total score = 18 → Conservative)
# ---------------------------------------------------------------------------
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


def _seed_products_and_scores(db_session, product_ids: list[str]) -> None:
    """Insert AssetClass records and AdvisorScore rows for each product_id."""
    from app.market_data.models import AssetClass
    from app.analytics.models import AdvisorScore

    today = date.today()
    for i, pid in enumerate(product_ids):
        # Insert asset class if not already present
        existing_ac = db_session.get(AssetClass, pid)
        if existing_ac is None:
            ac = AssetClass(
                id=pid,
                name=f"Test Product {i+1}",
                category="Equity" if i % 2 == 0 else "Debt",
                sub_category=None,
                sebi_risk_level=(i % 6) + 1,
                data_source="test",
                min_investment_inr=500.0,
                typical_exit_load_days=0,
                lock_in_days=0,
                expense_ratio_typical=0.5,
                is_crypto=False,
                is_active=True,
            )
            db_session.add(ac)

        # Insert advisor score
        score = AdvisorScore(
            product_id=pid,
            product_type="index",
            tax_bracket=0.30,
            time_horizon="long",
            computed_date=today,
            score_total=75.0,
            score_risk_adjusted=15.0,
            score_tax_yield=15.0,
            score_liquidity=15.0,
            score_expense=15.0,
            score_consistency=7.5,
            score_goal_fit=7.5,
            post_tax_return_3y=0.10,
        )
        db_session.add(score)

    db_session.commit()


def _make_advisor(session_factory, email: str, password: str, name: str) -> str:
    """Create an advisor and return the advisor_id (captured before session close)."""
    db = session_factory()
    advisor = create_advisor(db, email=email, password=password, name=name)
    advisor_id = str(advisor.id)  # capture before close to avoid DetachedInstanceError
    db.close()
    return advisor_id


@pytest.fixture
def setup():
    """Create in-memory DB + seeded reference data + TestClient."""
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

    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client, engine, Session
    app.dependency_overrides.clear()
    engine.dispose()


class TestAdvisorWorkflow:
    """Sequential integration tests exercising the full advisor workflow."""

    ADVISOR_EMAIL = "workflow@test.com"
    ADVISOR_PASSWORD = "Workflow123!"
    ADVISOR_NAME = "Workflow Advisor"
    PRODUCT_IDS = [f"test_product_{i}" for i in range(5)]

    def test_step1_login(self, setup):
        """POST /api/auth/login → 200, access_token present."""
        test_client, engine, Session = setup
        _make_advisor(Session, self.ADVISOR_EMAIL, self.ADVISOR_PASSWORD, self.ADVISOR_NAME)

        r = test_client.post("/api/auth/login", json={
            "email": self.ADVISOR_EMAIL,
            "password": self.ADVISOR_PASSWORD,
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["advisor"]["email"] == self.ADVISOR_EMAIL

    def test_step2_create_client(self, setup):
        """POST /api/clients → 201, client_id returned."""
        test_client, engine, Session = setup
        advisor_id = _make_advisor(Session, self.ADVISOR_EMAIL, self.ADVISOR_PASSWORD, self.ADVISOR_NAME)
        token = create_access_token(advisor_id)

        r = test_client.post(
            "/api/clients",
            json={"name": "Test Client", "age": 35, "tax_bracket": 0.30},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 201
        data = r.json()
        assert "id" in data
        assert data["name"] == "Test Client"

    def test_step3_dashboard(self, setup):
        """GET /api/products?tax_bracket=0.30&time_horizon=long → 200, products list has >= 1 item."""
        test_client, engine, Session = setup
        advisor_id = _make_advisor(Session, self.ADVISOR_EMAIL, self.ADVISOR_PASSWORD, self.ADVISOR_NAME)

        # Seed products via the same session factory (same engine / StaticPool → same DB)
        db = Session()
        _seed_products_and_scores(db, self.PRODUCT_IDS)
        db.close()

        token = create_access_token(advisor_id)
        r = test_client.get(
            "/api/products?tax_bracket=0.30&time_horizon=long",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        data = r.json()
        products = data.get("products", data) if isinstance(data, dict) else data
        assert len(products) >= 1

    def test_step4_verify_scoring(self, setup):
        """GET /api/products → each product has advisor_score field."""
        test_client, engine, Session = setup
        advisor_id = _make_advisor(Session, self.ADVISOR_EMAIL, self.ADVISOR_PASSWORD, self.ADVISOR_NAME)

        db = Session()
        _seed_products_and_scores(db, self.PRODUCT_IDS)
        db.close()

        token = create_access_token(advisor_id)
        r = test_client.get(
            "/api/products?tax_bracket=0.30&time_horizon=long",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        data = r.json()
        products = data.get("products", data) if isinstance(data, dict) else data
        assert len(products) >= 1
        for product in products:
            assert "advisor_score" in product, (
                f"advisor_score missing from product {product.get('id')}"
            )

    def test_step5_goal_creation(self, setup):
        """POST /api/goals → 201, goal_id returned."""
        test_client, engine, Session = setup
        advisor_id = _make_advisor(Session, self.ADVISOR_EMAIL, self.ADVISOR_PASSWORD, self.ADVISOR_NAME)
        token = create_access_token(advisor_id)

        # Create client first
        r = test_client.post(
            "/api/clients",
            json={"name": "Test Client", "age": 35, "tax_bracket": 0.30},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 201
        client_id = r.json()["id"]

        r = test_client.post(
            "/api/goals",
            json={
                "client_id": client_id,
                "name": "Retirement",
                "target_amount_inr": 10000000.0,
                "current_corpus_inr": 500000.0,
                "monthly_sip_inr": 25000.0,
                "annual_stepup_pct": 0.10,
                "inflation_rate": 0.06,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 201
        data = r.json()
        assert "id" in data
        assert data["name"] == "Retirement"

    def test_step6_goal_plan(self, setup):
        """GET /api/goals/{id}/plan → 200, nps_highlight field present."""
        test_client, engine, Session = setup
        advisor_id = _make_advisor(Session, self.ADVISOR_EMAIL, self.ADVISOR_PASSWORD, self.ADVISOR_NAME)
        token = create_access_token(advisor_id)

        r = test_client.post(
            "/api/clients",
            json={"name": "Test Client", "age": 35, "tax_bracket": 0.30},
            headers={"Authorization": f"Bearer {token}"},
        )
        client_id = r.json()["id"]

        r = test_client.post(
            "/api/goals",
            json={
                "client_id": client_id,
                "name": "Retirement",
                "target_amount_inr": 10000000.0,
                "current_corpus_inr": 500000.0,
                "monthly_sip_inr": 25000.0,
                "annual_stepup_pct": 0.10,
                "inflation_rate": 0.06,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        goal_id = r.json()["id"]

        r = test_client.get(
            f"/api/goals/{goal_id}/plan",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "nps_highlight" in data

    def test_step7_risk_questions(self, setup):
        """GET /api/risk-profiler/questions → 200, >= 15 questions."""
        test_client, engine, Session = setup
        advisor_id = _make_advisor(Session, self.ADVISOR_EMAIL, self.ADVISOR_PASSWORD, self.ADVISOR_NAME)
        token = create_access_token(advisor_id)

        r = test_client.get(
            "/api/risk-profiler/questions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        questions = r.json()
        assert isinstance(questions, list)
        assert len(questions) >= 15

    def test_step8_risk_profile(self, setup):
        """POST /api/risk-profiles with conservative answers → risk_category = 'Conservative'."""
        test_client, engine, Session = setup
        advisor_id = _make_advisor(Session, self.ADVISOR_EMAIL, self.ADVISOR_PASSWORD, self.ADVISOR_NAME)
        token = create_access_token(advisor_id)

        r = test_client.post(
            "/api/clients",
            json={"name": "Conservative Client", "age": 65, "tax_bracket": 0.30},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 201
        client_id = r.json()["id"]

        r = test_client.post(
            "/api/risk-profiles",
            json={
                "client_id": client_id,
                "responses": CONSERVATIVE_ANSWERS,
                "advisor_rationale": (
                    "Client is elderly with low income and high dependents — "
                    "conservative profile appropriate."
                ),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 201
        data = r.json()
        assert "id" in data
        assert data["risk_category"] == "Conservative"

    def test_step9_client_pdf(self, setup):
        """POST /api/pdf/client-report → 200, Content-Type: application/pdf, starts with %PDF."""
        test_client, engine, Session = setup
        advisor_id = _make_advisor(Session, self.ADVISOR_EMAIL, self.ADVISOR_PASSWORD, self.ADVISOR_NAME)

        db = Session()
        _seed_products_and_scores(db, self.PRODUCT_IDS)
        db.close()

        token = create_access_token(advisor_id)

        r = test_client.post(
            "/api/clients",
            json={"name": "PDF Client", "age": 40, "tax_bracket": 0.30},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 201
        client_id = r.json()["id"]

        r = test_client.post(
            "/api/pdf/client-report",
            json={
                "client_id": client_id,
                "product_ids": self.PRODUCT_IDS[:3],
                "tax_bracket": 0.30,
                "time_horizon": "long",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        assert "application/pdf" in r.headers.get("content-type", "")
        assert r.content[:4] == b"%PDF"

    def test_step10_compliance_pdf(self, setup):
        """POST /api/pdf/compliance-pack → 200, Content-Type: application/pdf."""
        test_client, engine, Session = setup
        advisor_id = _make_advisor(Session, self.ADVISOR_EMAIL, self.ADVISOR_PASSWORD, self.ADVISOR_NAME)
        token = create_access_token(advisor_id)

        r = test_client.post(
            "/api/clients",
            json={"name": "Compliance Client", "age": 55, "tax_bracket": 0.30},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 201
        client_id = r.json()["id"]

        r = test_client.post(
            "/api/risk-profiles",
            json={
                "client_id": client_id,
                "responses": CONSERVATIVE_ANSWERS,
                "advisor_rationale": "Client requires conservative allocation per SEBI guidelines.",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 201
        risk_profile_id = r.json()["id"]

        r = test_client.post(
            "/api/pdf/compliance-pack",
            json={"risk_profile_id": risk_profile_id},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        assert "application/pdf" in r.headers.get("content-type", "")
        assert r.content[:4] == b"%PDF"
