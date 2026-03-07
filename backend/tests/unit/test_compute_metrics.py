from __future__ import annotations
import pytest
from datetime import date, timedelta
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.market_data.models import MutualFund, NavHistory
from app.analytics.models import ComputedMetric


@pytest.fixture
def db_session():
    # Import all models so metadata is fully populated
    import app.auth.models  # noqa: F401
    import app.market_data.models  # noqa: F401
    import app.analytics.models  # noqa: F401
    import app.goals.models  # noqa: F401
    import app.risk_profiler.models  # noqa: F401

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


def _seed_fund_with_nav(session, scheme_code: str, cagr: float, n_days: int):
    """Helper: add a MutualFund + NAV history rows (weekdays only)."""
    fund = MutualFund(scheme_code=scheme_code, scheme_name=f"Fund {scheme_code}", is_active=True)
    session.add(fund)
    session.flush()

    daily_return = (1 + cagr) ** (1 / 252) - 1
    start_date = date(2019, 1, 1)
    nav = 100.0
    added = 0
    day_offset = 0
    while added < n_days:
        d = start_date + timedelta(days=day_offset)
        day_offset += 1
        if d.weekday() < 5:  # Weekdays only
            nav *= (1 + daily_return)
            session.add(NavHistory(scheme_code=scheme_code, nav_date=d, nav=round(nav, 4)))
            added += 1
    session.commit()


def _seed_flat_fund_with_nav(session, scheme_code: str, n_days: int):
    """Helper: add a MutualFund with perfectly flat NAV (constant 100.0) on weekdays."""
    fund = MutualFund(scheme_code=scheme_code, scheme_name=f"Fund {scheme_code}", is_active=True)
    session.add(fund)
    session.flush()

    start_date = date(2019, 1, 1)
    added = 0
    day_offset = 0
    while added < n_days:
        d = start_date + timedelta(days=day_offset)
        day_offset += 1
        if d.weekday() < 5:
            session.add(NavHistory(scheme_code=scheme_code, nav_date=d, nav=100.0))
            added += 1
    session.commit()


def test_compute_metrics_5_schemes(db_session):
    """Seed 5 funds with 3Y+ history (756 days), run job, assert 5 rows with today's date."""
    from app.jobs.compute_metrics import compute_all_product_metrics

    for i in range(5):
        _seed_fund_with_nav(db_session, f"FUND{i:03d}", cagr=0.12, n_days=756)

    result = compute_all_product_metrics(db_session)

    rows = db_session.query(ComputedMetric).all()
    assert len(rows) == 5, f"Expected 5 rows, got {len(rows)}"
    today = date.today()
    for row in rows:
        assert row.computed_date == today
    assert result["processed"] == 5
    assert result["errors"] == 0


def test_computed_metrics_cagr_not_none(db_session):
    """After running, each row should have non-None cagr_3y, std_dev_3y, sharpe_3y."""
    from app.jobs.compute_metrics import compute_all_product_metrics

    for i in range(3):
        _seed_fund_with_nav(db_session, f"CAGR{i:03d}", cagr=0.10, n_days=756)

    compute_all_product_metrics(db_session)

    rows = db_session.query(ComputedMetric).all()
    assert len(rows) == 3
    for row in rows:
        assert row.cagr_3y is not None, f"cagr_3y is None for {row.product_id}"
        assert row.std_dev_3y is not None, f"std_dev_3y is None for {row.product_id}"
        assert row.sharpe_3y is not None, f"sharpe_3y is None for {row.product_id}"


def test_scheme_with_less_than_3y_history_cagr5y_none(db_session):
    """Fund with only 500 days (< 3Y=756): row exists but cagr_5y is None; cagr_1y may be non-None."""
    from app.jobs.compute_metrics import compute_all_product_metrics

    _seed_fund_with_nav(db_session, "SHORT001", cagr=0.08, n_days=500)

    compute_all_product_metrics(db_session)

    rows = db_session.query(ComputedMetric).filter(ComputedMetric.product_id == "SHORT001").all()
    assert len(rows) == 1, f"Expected 1 row, got {len(rows)}"
    row = rows[0]
    assert row.cagr_5y is None, f"Expected cagr_5y to be None, got {row.cagr_5y}"
    # cagr_1y should be computable since 500 > 252
    assert row.cagr_1y is not None, f"Expected cagr_1y to be non-None for 500-day series"


def test_idempotent_no_duplicate(db_session):
    """Run job twice on same day; assert computed_metrics still has same count (upsert)."""
    from app.jobs.compute_metrics import compute_all_product_metrics

    for i in range(3):
        _seed_fund_with_nav(db_session, f"IDEM{i:03d}", cagr=0.09, n_days=756)

    compute_all_product_metrics(db_session)
    count_after_first = db_session.query(ComputedMetric).count()

    compute_all_product_metrics(db_session)
    count_after_second = db_session.query(ComputedMetric).count()

    assert count_after_first == count_after_second, (
        f"Row count changed on second run: {count_after_first} -> {count_after_second}"
    )
    assert count_after_first == 3


def test_zero_variance_sharpe_none(db_session):
    """PPF-like fund with perfectly flat NAV for 756 days: sharpe_3y should be None."""
    from app.jobs.compute_metrics import compute_all_product_metrics

    _seed_flat_fund_with_nav(db_session, "FLAT001", n_days=756)

    compute_all_product_metrics(db_session)

    rows = db_session.query(ComputedMetric).filter(ComputedMetric.product_id == "FLAT001").all()
    assert len(rows) == 1, f"Expected 1 row, got {len(rows)}"
    row = rows[0]
    assert row.sharpe_3y is None, (
        f"Expected sharpe_3y to be None for zero-variance series, got {row.sharpe_3y}"
    )
