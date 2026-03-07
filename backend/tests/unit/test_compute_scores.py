"""Unit tests for the nightly advisor score computation job."""
from __future__ import annotations
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.market_data.models import AssetClass
from app.analytics.models import ComputedMetric, AdvisorScore
from app.jobs.compute_scores import compute_all_scores


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


def _seed_5_products(session):
    """Seed 5 asset classes with computed metrics."""
    specs = [
        ("prod_eq1", "Equity 1", "Equity", 5, 3, 0.012),
        ("prod_eq2", "Equity 2", "Equity", 5, 3, 0.010),
        ("prod_eq3", "Equity 3", "Equity", 4, 3, 0.008),
        ("prod_ppf", "PPF", "Fixed", 1, 5475, None),
        ("prod_liquid", "Liquid Fund", "Debt", 1, 0, 0.004),
    ]
    today = date.today()
    for i, (pid, name, cat, risk, lock, er) in enumerate(specs):
        session.add(AssetClass(
            id=pid, name=name, category=cat,
            sebi_risk_level=risk, lock_in_days=lock,
            expense_ratio_typical=er,
            is_active=True, is_crypto=False,
        ))
        is_ppf = pid == "prod_ppf"
        session.add(ComputedMetric(
            product_id=pid, product_type="index",
            computed_date=today,
            cagr_1y=0.10 + i * 0.01,
            cagr_3y=0.09 + i * 0.01,
            cagr_5y=0.08 + i * 0.01,
            cagr_10y=None,
            std_dev_3y=None if is_ppf else 0.15 + i * 0.02,
            sharpe_3y=None if is_ppf else 0.50 + i * 0.10,
            sortino_3y=None if is_ppf else 0.60 + i * 0.10,
            max_drawdown_5y=-0.20 - i * 0.05,
            expense_ratio=er,
        ))
    session.commit()


def test_compute_all_scores_5_products_75_rows(db_session):
    """5 products × 5 brackets × 3 horizons = 75 rows."""
    _seed_5_products(db_session)
    result = compute_all_scores(db_session)
    count = db_session.query(AdvisorScore).count()
    assert count == 75, f"Expected 75, got {count}"


def test_score_total_in_range(db_session):
    """All score_total values must be in [0, 100]."""
    _seed_5_products(db_session)
    compute_all_scores(db_session)
    scores = db_session.query(AdvisorScore.score_total).all()
    for (s,) in scores:
        assert 0.0 <= s <= 100.0, f"score_total {s} out of range"


def test_idempotent_same_day(db_session):
    """Running twice on the same day must not create duplicate rows."""
    _seed_5_products(db_session)
    compute_all_scores(db_session)
    compute_all_scores(db_session)
    count = db_session.query(AdvisorScore).count()
    assert count == 75


def test_compute_scores_returns_summary(db_session):
    """Return dict has total_scores=75 and products=5."""
    _seed_5_products(db_session)
    result = compute_all_scores(db_session)
    assert result["total_scores"] == 75
    assert result["products"] == 5


def test_empty_metrics_returns_zero(db_session):
    """No computed_metrics → no advisor_scores, returns 0."""
    result = compute_all_scores(db_session)
    assert result["total_scores"] == 0
    assert db_session.query(AdvisorScore).count() == 0


def test_scheduler_has_six_jobs():
    """Scheduler must now have 6 registered jobs (added compute_scores)."""
    from app.jobs.scheduler import scheduler
    jobs = scheduler.get_jobs()
    assert len(jobs) == 6
    job_ids = {j.id for j in jobs}
    assert "compute_scores" in job_ids
