"""Unit tests for mfapi.in historical NAV backfill."""
from __future__ import annotations
from datetime import date
from unittest.mock import patch, MagicMock

from app.jobs.ingest_mfapi import fetch_scheme_history, backfill_historical_nav


def make_mock_mfapi_response(scheme_code: str, num_rows: int = 1000) -> dict:
    """Build a mock mfapi.in JSON response with N historical NAV rows."""
    from datetime import timedelta
    base_date = date(2025, 2, 21)
    data = []
    for i in range(num_rows):
        d = base_date - timedelta(days=i)
        # Skip weekends for realism
        if d.weekday() < 5:
            data.append({"date": d.strftime("%d-%m-%Y"), "nav": f"{50.0 + i * 0.01:.4f}"})
    return {
        "meta": {"scheme_code": int(scheme_code), "scheme_name": f"Test Fund {scheme_code}"},
        "data": data,
    }


def test_fetch_scheme_history_parses_1000_rows():
    mock_response = make_mock_mfapi_response("119551", 1000)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response

    with patch("requests.get", return_value=mock_resp):
        records = fetch_scheme_history("119551")

    assert len(records) > 0
    assert all(r["scheme_code"] == "119551" for r in records)


def test_fetch_scheme_history_dates_are_date_objects():
    mock_response = make_mock_mfapi_response("119551", 10)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response

    with patch("requests.get", return_value=mock_resp):
        records = fetch_scheme_history("119551")

    for r in records:
        assert isinstance(r["nav_date"], date)


def test_fetch_scheme_history_date_format_dd_mm_yyyy():
    """mfapi.in uses DD-MM-YYYY — not DD-Mon-YYYY like AMFI."""
    mock_response = {"meta": {}, "data": [{"date": "21-02-2025", "nav": "62.4567"}]}
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response

    with patch("requests.get", return_value=mock_resp):
        records = fetch_scheme_history("119551")

    assert len(records) == 1
    assert records[0]["nav_date"] == date(2025, 2, 21)


def test_fetch_scheme_history_handles_429_with_backoff():
    """HTTP 429 triggers backoff — verify it doesn't crash."""
    mock_resp_429 = MagicMock()
    mock_resp_429.status_code = 429

    mock_resp_ok = MagicMock()
    mock_resp_ok.status_code = 200
    mock_resp_ok.json.return_value = {"meta": {}, "data": [{"date": "21-02-2025", "nav": "62.45"}]}

    with patch("requests.get", side_effect=[mock_resp_429, mock_resp_ok]), \
         patch("time.sleep"):  # Don't actually sleep in tests
        records = fetch_scheme_history("119551")

    assert len(records) == 1


def test_fetch_scheme_history_handles_network_error():
    """Network error returns empty list — does not raise."""
    import requests as req
    with patch("requests.get", side_effect=req.exceptions.ConnectionError("No network")):
        records = fetch_scheme_history("119551")
    assert records == []


def test_backfill_is_idempotent(db_session):
    """Running backfill twice inserts 0 on second run."""
    mock_response = make_mock_mfapi_response("119551", 5)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_response

    # Need a scheme in mutual_funds first
    from app.market_data.models import MutualFund
    fund = MutualFund(scheme_code="119551", scheme_name="Test Fund", is_active=True, direct_plan=False)
    db_session.add(fund)
    db_session.commit()

    with patch("requests.get", return_value=mock_resp):
        inserted1, _ = backfill_historical_nav("119551", db_session)
        inserted2, skipped2 = backfill_historical_nav("119551", db_session)

    assert inserted1 > 0
    assert inserted2 == 0
    assert skipped2 > 0
