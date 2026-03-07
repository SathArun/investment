from __future__ import annotations
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from jose import jwt
from unittest.mock import patch

from app.main import app
from app.db.base import Base, get_db
from app.config import settings
from app.analytics.models import AdvisorScore, ComputedMetric
from app.market_data.models import AssetClass, MutualFund, NavHistory, IndexHistory


def make_test_token(advisor_id: str = "test_advisor") -> str:
    return jwt.encode({"sub": advisor_id}, settings.JWT_SECRET_KEY, algorithm="HS256")


@pytest.fixture
def test_db():
    # StaticPool ensures all connections share the same in-memory SQLite database
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


# Prevent APScheduler from starting/stopping during integration tests
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


def seed_products(session):
    """Seed test data: 3 asset classes + advisor scores."""
    ac1 = AssetClass(id="eq_largecap", name="Large Cap Equity", category="Equity",
                     sebi_risk_level=5, lock_in_days=3, is_active=True, is_crypto=False)
    ac2 = AssetClass(id="debt_liquid", name="Liquid Fund", category="Debt",
                     sebi_risk_level=1, lock_in_days=0, is_active=True, is_crypto=False)
    ac3 = AssetClass(id="ppf", name="PPF", category="Fixed",
                     sebi_risk_level=1, lock_in_days=5475, is_active=True, is_crypto=False)
    session.add_all([ac1, ac2, ac3])
    session.flush()

    today = date.today()
    for prod_id, score in [("eq_largecap", 75.0), ("debt_liquid", 60.0), ("ppf", 55.0)]:
        session.add(AdvisorScore(
            product_id=prod_id, product_type="index",
            tax_bracket=0.30, time_horizon="long",
            computed_date=today,
            score_total=score,
            score_risk_adjusted=score, score_tax_yield=score,
            score_liquidity=score, score_expense=score,
            score_consistency=score, score_goal_fit=score,
            post_tax_return_3y=0.08,
        ))
    session.commit()


def test_get_products_returns_200(client):
    test_client, session = client
    seed_products(session)
    token = make_test_token()
    response = test_client.get(
        "/api/products?tax_bracket=0.30&time_horizon=long",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert len(data["products"]) == 3


def test_get_products_sorted_by_score(client):
    test_client, session = client
    seed_products(session)
    token = make_test_token()
    response = test_client.get(
        "/api/products?tax_bracket=0.30&time_horizon=long&sort_by=score_total&sort_dir=desc",
        headers={"Authorization": f"Bearer {token}"},
    )
    products = response.json()["products"]
    scores = [p["advisor_score"] for p in products]
    assert scores == sorted(scores, reverse=True)


def test_get_products_requires_auth(client):
    test_client, session = client
    seed_products(session)
    response = test_client.get("/api/products?tax_bracket=0.30&time_horizon=long")
    assert response.status_code == 403  # No auth header -> 403 from HTTPBearer


def test_get_products_invalid_token_401(client):
    test_client, session = client
    seed_products(session)
    response = test_client.get(
        "/api/products",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401


def test_data_freshness_in_response(client):
    test_client, session = client
    seed_products(session)
    token = make_test_token()
    response = test_client.get(
        "/api/products?tax_bracket=0.30&time_horizon=long",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()
    assert "data_freshness" in data
    assert "amfi" in data["data_freshness"]


def test_product_history_404_for_unknown(client):
    test_client, session = client
    token = make_test_token()
    response = test_client.get(
        "/api/products/nonexistent_fund/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_product_history_returns_series(client):
    test_client, session = client
    # Seed a mutual fund with nav history
    fund = MutualFund(scheme_code="119551", scheme_name="Test Fund", is_active=True)
    session.add(fund)
    session.flush()
    start = date(2022, 1, 3)
    for i in range(500):
        d = date.fromordinal(start.toordinal() + i)
        if d.weekday() < 5:
            session.add(NavHistory(scheme_code="119551", nav_date=d, nav=100.0 + i * 0.05))
    session.commit()

    token = make_test_token()
    response = test_client.get(
        "/api/products/119551/history?period=5y",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "returns_series" in data
    assert "rolling_1y" in data
    assert len(data["returns_series"]) > 100
