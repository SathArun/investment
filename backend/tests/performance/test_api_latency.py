"""Performance benchmarks for India Investment Analyzer API endpoints.

T9.4 targets:
- GET /api/products < 200ms average over 10 requests
- PDF generation for 5-product client report < 10 seconds
"""
from __future__ import annotations
import time
import uuid
from datetime import date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.main import app
from app.db.base import Base, get_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def no_scheduler():
    with patch("app.jobs.scheduler.start", lambda: None), \
         patch("app.jobs.scheduler.stop", lambda: None):
        yield


@pytest.fixture
def perf_db():
    """In-memory SQLite engine seeded with reference + performance test data."""
    # Ensure all models are registered before create_all
    import app.auth.models  # noqa: F401
    import app.market_data.models  # noqa: F401
    import app.analytics.models  # noqa: F401
    import app.goals.models  # noqa: F401
    import app.risk_profiler.models  # noqa: F401

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    yield session, engine
    session.close()
    engine.dispose()


@pytest.fixture
def perf_client(perf_db):
    """TestClient with seeded data for performance testing."""
    session, engine = perf_db
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app), session
    app.dependency_overrides.clear()


def _seed_perf_data(session):
    """Seed advisor, asset classes, mutual funds, advisor_scores, client for perf tests.

    Returns (advisor, access_token, product_ids, client_id).
    """
    from app.auth.service import create_advisor, create_access_token
    from app.db.seed import seed_asset_classes, seed_tax_rules
    from app.analytics.models import AdvisorScore
    from app.market_data.models import AssetClass
    from app.goals.models import Client

    seed_asset_classes(session)
    seed_tax_rules(session)

    advisor = create_advisor(
        session,
        email=f"perf_{uuid.uuid4().hex[:8]}@test.com",
        password="pass123!",
        name="Perf Advisor",
    )
    token = create_access_token(advisor.id)

    # Use seeded asset class IDs as product IDs (type = "index")
    asset_classes = session.query(AssetClass).limit(20).all()
    product_ids = [ac.id for ac in asset_classes[:20]]

    today = date.today()
    for pid in product_ids:
        score = AdvisorScore(
            product_id=pid,
            product_type="index",
            tax_bracket=0.30,
            time_horizon="long",
            computed_date=today,
            score_total=75.0,
            score_risk_adjusted=70.0,
            score_tax_yield=80.0,
            score_liquidity=65.0,
            score_expense=85.0,
            score_consistency=72.0,
            score_goal_fit=78.0,
            post_tax_return_3y=0.10,
        )
        session.add(score)

    client = Client(
        id=str(uuid.uuid4()),
        advisor_id=advisor.id,
        name="Perf Client",
        age=35,
        tax_bracket=0.30,
    )
    session.add(client)
    session.commit()

    return advisor, token, product_ids, client.id


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_products_api_under_200ms(perf_client):
    """GET /api/products should respond in < 200ms on average over 10 requests."""
    test_client, session = perf_client
    _, token, _, _ = _seed_perf_data(session)

    times = []
    for _ in range(10):
        start = time.perf_counter()
        r = test_client.get(
            "/api/products?tax_bracket=0.30&time_horizon=long",
            headers={"Authorization": f"Bearer {token}"},
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        times.append(elapsed_ms)

    avg = sum(times) / len(times)
    print(f"\nProducts API avg latency: {avg:.1f}ms (min={min(times):.1f}ms, max={max(times):.1f}ms)")
    assert avg < 200, f"Average response time {avg:.1f}ms exceeds 200ms target"


def test_pdf_generation_under_10s(perf_client):
    """PDF generation for 5-product client report should complete in < 10 seconds."""
    test_client, session = perf_client
    _, token, product_ids, client_id = _seed_perf_data(session)

    start = time.perf_counter()
    r = test_client.post(
        "/api/pdf/client-report",
        json={
            "client_id": client_id,
            "product_ids": product_ids[:5],
            "tax_bracket": 0.30,
            "time_horizon": "long",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    elapsed = time.perf_counter() - start

    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    print(f"\nPDF generation time: {elapsed:.2f}s")
    assert elapsed < 10, f"PDF generation took {elapsed:.1f}s, exceeds 10s target"
