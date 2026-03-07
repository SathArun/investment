"""Root conftest: ensures all tables are created before any test runs."""
import os
import sys

# Ensure backend directory is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pytest


def pytest_configure(config):
    """Create all tables at test session start using SQLAlchemy metadata."""
    # Import all models to register them on Base.metadata
    import app.auth.models  # noqa: F401
    import app.market_data.models  # noqa: F401
    import app.analytics.models  # noqa: F401
    import app.goals.models  # noqa: F401
    import app.risk_profiler.models  # noqa: F401

    from app.db.base import Base, engine
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a SQLAlchemy session backed by a fresh in-memory SQLite DB.

    Each test gets an isolated database — tables are created and reference data
    is seeded so tests that query seed data work without depending on an
    external database file.  Committed data is discarded when the fixture tears
    down.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Import all models so metadata is populated
    import app.auth.models  # noqa: F401
    import app.market_data.models  # noqa: F401
    import app.analytics.models  # noqa: F401
    import app.goals.models  # noqa: F401
    import app.risk_profiler.models  # noqa: F401
    from app.db.base import Base
    from app.db.seed import seed_asset_classes, seed_tax_rules

    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSession()

    # Pre-seed reference data so tests that query seed tables work correctly
    seed_asset_classes(session)
    seed_tax_rules(session)

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()
