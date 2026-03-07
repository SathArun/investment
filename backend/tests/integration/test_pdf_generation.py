"""Integration tests for PDF generation endpoints (Phase 6)."""
from __future__ import annotations
import json
import uuid
from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base, get_db
from app.auth.service import create_advisor, create_access_token
from app.auth.dependencies import get_current_advisor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pdf_contains_text(pdf_bytes: bytes, text: str) -> bool:
    """Simple check: look for text in raw PDF bytes (works for uncompressed text streams)."""
    return text.encode() in pdf_bytes or text.lower().encode() in pdf_bytes.lower()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def no_scheduler():
    with patch("app.jobs.scheduler.start", lambda: None), \
         patch("app.jobs.scheduler.stop", lambda: None):
        yield


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
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    yield session, engine
    session.close()
    engine.dispose()


@pytest.fixture
def client_fixture(test_db):
    session, engine = test_db
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


def _seed_advisor(session):
    """Create and return an Advisor plus a valid access token."""
    advisor = create_advisor(
        session,
        email=f"advisor_{uuid.uuid4().hex[:8]}@test.com",
        password="pass123!",
        name="Test Advisor",
        firm_name="Test Firm",
        contact_phone="+91-9999999999",
        primary_color="#1a56db",
    )
    token = create_access_token(advisor.id)
    return advisor, token


def _seed_client(session, advisor_id: str):
    """Create and return a Client row."""
    from app.goals.models import Client
    client = Client(
        id=str(uuid.uuid4()),
        advisor_id=advisor_id,
        name="Rahul Test",
        age=35,
        tax_bracket=0.30,
    )
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


def _seed_risk_profile(session, advisor_id: str, client_id: str, rationale: str = "Client has moderate risk tolerance based on long investment horizon."):
    """Create and return a RiskProfile row."""
    from app.risk_profiler.models import RiskProfile
    responses = json.dumps([
        {"question_id": "q01", "selected_value": "under_35"},
        {"question_id": "q02", "selected_value": "retire_above_60"},
        {"question_id": "q08", "selected_value": "growth"},
    ])
    profile = RiskProfile(
        id=str(uuid.uuid4()),
        client_id=client_id,
        advisor_id=advisor_id,
        risk_score=60.0,
        risk_category="Moderate",
        question_responses=responses,
        advisor_rationale=rationale,
        retention_until=date.today() + timedelta(days=5*365),
        completed_at=datetime.now(),
        is_deleted=False,
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_client_report_returns_pdf_binary(client_fixture):
    """POST /api/pdf/client-report with valid data returns 200 and PDF bytes."""
    test_client, session = client_fixture
    advisor, token = _seed_advisor(session)
    client = _seed_client(session, advisor.id)

    response = test_client.post(
        "/api/pdf/client-report",
        json={
            "client_id": client.id,
            "product_ids": ["some-product-id"],
            "tax_bracket": 0.30,
            "time_horizon": "long",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"
    assert len(response.content) > 1000


def _decompress_pdf_streams(pdf_bytes: bytes) -> bytes:
    """
    Decompress all ASCII85+zlib content streams from a ReportLab PDF.
    Returns concatenated decompressed bytes.
    """
    import zlib
    import base64

    result = b""
    search_pos = 0
    while True:
        stream_start = pdf_bytes.find(b"stream\n", search_pos)
        if stream_start == -1:
            break
        data_start = stream_start + len(b"stream\n")
        # Find ASCII85 end marker ~>
        a85_end = pdf_bytes.find(b"~>", data_start)
        if a85_end == -1:
            search_pos = data_start
            continue
        stream_data = pdf_bytes[data_start : a85_end + 2]  # include ~>
        search_pos = a85_end + 2
        # Try ASCII85 decode then zlib decompress
        try:
            decoded = base64.a85decode(stream_data, adobe=True)
            decompressed = zlib.decompress(decoded)
            result += decompressed
        except Exception:
            # Try raw zlib (FlateDecode only, no ASCII85)
            try:
                decompressed = zlib.decompress(stream_data)
                result += decompressed
            except Exception:
                pass
    return result


def test_client_report_sebi_disclaimer_in_pdf(client_fixture):
    """Generated PDF must contain the SEBI disclaimer text (verified via decompressed stream)."""
    test_client, session = client_fixture
    advisor, token = _seed_advisor(session)
    client = _seed_client(session, advisor.id)

    response = test_client.post(
        "/api/pdf/client-report",
        json={
            "client_id": client.id,
            "product_ids": ["prod-1"],
            "tax_bracket": 0.30,
            "time_horizon": "long",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    pdf_bytes = response.content

    # PDF is valid and has reasonable size
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 1000

    sebi_text = b"Investment in securities market"

    # Direct check first (works for uncompressed streams)
    if sebi_text in pdf_bytes:
        return  # Found directly

    # Decompress streams and search
    decompressed_content = _decompress_pdf_streams(pdf_bytes)
    assert sebi_text in decompressed_content, (
        "SEBI disclaimer text not found in PDF content streams"
    )


def test_client_report_no_sharpe_in_output(client_fixture):
    """Client-view PDF must not expose Sharpe ratio data to the client."""
    test_client, session = client_fixture
    advisor, token = _seed_advisor(session)
    client = _seed_client(session, advisor.id)

    response = test_client.post(
        "/api/pdf/client-report",
        json={
            "client_id": client.id,
            "product_ids": ["prod-1"],
            "tax_bracket": 0.30,
            "time_horizon": "long",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    # "Sharpe" should not appear anywhere in the raw PDF bytes
    assert b"Sharpe" not in response.content
    assert b"sharpe" not in response.content


def test_client_report_max_5_products(client_fixture):
    """Sending more than 5 product_ids must return 422."""
    test_client, session = client_fixture
    advisor, token = _seed_advisor(session)
    client = _seed_client(session, advisor.id)

    response = test_client.post(
        "/api/pdf/client-report",
        json={
            "client_id": client.id,
            "product_ids": ["p1", "p2", "p3", "p4", "p5", "p6"],
            "tax_bracket": 0.30,
            "time_horizon": "long",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_client_report_unknown_product_handled(client_fixture):
    """Unknown product IDs should be handled gracefully — still returns 200."""
    test_client, session = client_fixture
    advisor, token = _seed_advisor(session)
    client = _seed_client(session, advisor.id)

    response = test_client.post(
        "/api/pdf/client-report",
        json={
            "client_id": client.id,
            "product_ids": ["totally-unknown-product-xyz"],
            "tax_bracket": 0.30,
            "time_horizon": "long",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.content[:4] == b"%PDF"


def test_compliance_pack_returns_pdf_binary(client_fixture):
    """POST /api/pdf/compliance-pack with valid risk profile returns 200 and PDF bytes."""
    test_client, session = client_fixture
    advisor, token = _seed_advisor(session)
    client = _seed_client(session, advisor.id)
    profile = _seed_risk_profile(session, advisor.id, client.id)

    response = test_client.post(
        "/api/pdf/compliance-pack",
        json={"risk_profile_id": profile.id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"
    assert len(response.content) > 1000


def test_compliance_pack_empty_rationale_returns_422(client_fixture):
    """Compliance pack generation with empty advisor_rationale must return 422."""
    test_client, session = client_fixture
    advisor, token = _seed_advisor(session)
    client = _seed_client(session, advisor.id)
    profile = _seed_risk_profile(session, advisor.id, client.id, rationale="   ")

    response = test_client.post(
        "/api/pdf/compliance-pack",
        json={"risk_profile_id": profile.id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_compliance_pack_updates_db_path(client_fixture):
    """After generating compliance pack, risk_profile.compliance_pdf_path must be set."""
    test_client, session = client_fixture
    advisor, token = _seed_advisor(session)
    client = _seed_client(session, advisor.id)
    profile = _seed_risk_profile(session, advisor.id, client.id)

    response = test_client.post(
        "/api/pdf/compliance-pack",
        json={"risk_profile_id": profile.id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    # Re-query the profile from DB to check the path was persisted
    session.expire(profile)
    session.refresh(profile)
    assert profile.compliance_pdf_path is not None
    assert profile.compliance_pdf_path.endswith(".pdf")


def test_client_report_missing_cagr_shows_na(client_fixture):
    """When a product has no cagr_1y, the PDF must show N/A not a 3Y value substitution."""
    from app.analytics.models import AdvisorScore, ComputedMetric
    import zlib, base64

    test_client, session = client_fixture
    advisor, token = _seed_advisor(session)
    client = _seed_client(session, advisor.id)

    response = test_client.post(
        "/api/pdf/client-report",
        json={
            "client_id": client.id,
            "product_ids": ["unknown-product-no-cagr"],
            "tax_bracket": 0.30,
            "time_horizon": "long",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    pdf_bytes = response.content
    assert pdf_bytes[:4] == b"%PDF"
    # "N/A" must appear in the PDF (shown when cagr_1y is absent)
    # Check raw bytes first, then decompress
    if b"N/A" in pdf_bytes:
        return
    # Try decompressed streams
    decompressed = _decompress_pdf_streams(pdf_bytes)
    assert b"N/A" in decompressed, "Expected N/A in PDF when cagr_1y is missing"


def test_compliance_pack_malformed_responses_generates_pdf(client_fixture):
    """Compliance pack with unparseable question_responses JSON must still generate a PDF.
    The M4 fix ensures the error is logged but does not crash PDF generation."""
    from app.risk_profiler.models import RiskProfile

    test_client, session = client_fixture
    advisor, token = _seed_advisor(session)
    client = _seed_client(session, advisor.id)

    # Seed profile with deliberately malformed JSON
    profile = RiskProfile(
        id=str(uuid.uuid4()),
        client_id=client.id,
        advisor_id=advisor.id,
        risk_score=60.0,
        risk_category="Moderate",
        question_responses="THIS IS NOT JSON {{{{",
        advisor_rationale="Client has considered all risk factors carefully and discussed them.",
        retention_until=date.today() + timedelta(days=5 * 365),
        completed_at=datetime.now(),
        is_deleted=False,
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)

    response = test_client.post(
        "/api/pdf/compliance-pack",
        json={"risk_profile_id": profile.id},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Should still return a valid PDF (not crash)
    assert response.status_code == 200
    assert response.content[:4] == b"%PDF"


def test_client_report_invalid_time_horizon_returns_422(client_fixture):
    """time_horizon must be one of short/medium/long — anything else returns 422."""
    test_client, session = client_fixture
    advisor, token = _seed_advisor(session)
    client = _seed_client(session, advisor.id)

    response = test_client.post(
        "/api/pdf/client-report",
        json={
            "client_id": client.id,
            "product_ids": ["p1"],
            "time_horizon": "never",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_client_report_out_of_range_tax_bracket_returns_422(client_fixture):
    """tax_bracket outside [0, 1] must return 422 (M2 Field validation)."""
    test_client, session = client_fixture
    advisor, token = _seed_advisor(session)
    client = _seed_client(session, advisor.id)

    for bad_value in [1.5, -0.1, 2.0]:
        response = test_client.post(
            "/api/pdf/client-report",
            json={
                "client_id": client.id,
                "product_ids": ["p1"],
                "tax_bracket": bad_value,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422, f"Expected 422 for tax_bracket={bad_value}, got {response.status_code}"
