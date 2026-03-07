"""Unit tests for yfinance equity/index ingestion."""
from __future__ import annotations
from datetime import date
from unittest.mock import patch, MagicMock
import pandas as pd

from app.jobs.ingest_equity import fetch_index_history, load_ticker_config


def make_mock_yf_data(rows: int = 10) -> pd.DataFrame:
    """Create a mock yfinance DataFrame."""
    import pandas as pd
    dates = pd.date_range(start="2024-01-02", periods=rows, freq="B")  # Business days
    data = pd.DataFrame({"Close": [100.0 + i for i in range(rows)]}, index=dates)
    return data


def test_load_ticker_config_has_required_tickers():
    configs = load_ticker_config()
    tickers = [c["ticker"] for c in configs]
    assert "^NSEI" in tickers, "Nifty 50 must be in ticker config"
    assert len(configs) >= 5


def test_fetch_index_history_parses_mock_data():
    mock_data = make_mock_yf_data(100)
    with patch("yfinance.download", return_value=mock_data):
        records = fetch_index_history("^NSEI", period="1y")
    assert len(records) == 100
    assert all(r["ticker"] == "^NSEI" for r in records)
    assert all(isinstance(r["price_date"], date) for r in records)
    assert all(r["close_price"] > 0 for r in records)


def test_fetch_index_history_no_weekends():
    """Business day frequency should have no Saturday/Sunday."""
    mock_data = make_mock_yf_data(50)
    with patch("yfinance.download", return_value=mock_data):
        records = fetch_index_history("^NSEI")
    for r in records:
        weekday = r["price_date"].weekday()
        assert weekday < 5, f"Weekend date found: {r['price_date']}"


def test_fetch_index_history_handles_empty_gracefully():
    with patch("yfinance.download", return_value=pd.DataFrame()):
        records = fetch_index_history("INVALID.TICKER")
    assert records == []


def test_fetch_index_history_handles_error_gracefully():
    with patch("yfinance.download", side_effect=Exception("Network error")):
        records = fetch_index_history("^NSEI")
    assert records == []
