"""Unit tests for data ingestion parsers."""
from __future__ import annotations
from datetime import date
from app.jobs.ingest_amfi import parse_amfi_nav

AMFI_FIXTURE = """Open Ended Schemes(Debt Schemes - Low Duration Fund);
Scheme Code|ISIN Div Payout/ISIN Growth|ISIN Div Reinvestment|Scheme Name|Net Asset Value|Date
119551|INF879O01019|INF879O01019|Aditya Birla SL Low Duration-Direct-Growth|62.4567|21-Feb-2025
119552|INF879O01027|INF879O01027|Aditya Birla SL Low Duration-Regular-Growth|54.1234|21-Feb-2025
119553|INF879O01035|INF879O01035|Aditya Birla SL Money Manager-Direct-Growth|344.5678|21-Feb-2025
119554|INF879O01043|INF879O01043|Aditya Birla SL Money Manager-Regular-Growth|298.7654|21-Feb-2025
119555|INF879O01050|INF879O01050|Aditya Birla SL Short Term-Direct-Growth|45.2345|21-Feb-2025
MALFORMED_LINE_MISSING_FIELDS|bad
Open Ended Schemes(Equity Schemes - Large Cap Fund);
119556|INF879O01068|INF879O01068|HDFC Top 100-Direct-Growth|987.4321|21-Feb-2025
119557|INF879O01076|INF879O01076|HDFC Top 100-Regular-Growth|756.8765|21-Feb-2025
119558|INF879O01084|INF879O01084|ICICI Pru Bluechip-Direct-Growth|123.4567|21-Feb-2025
119559|INF879O01092|INF879O01092|ICICI Pru Bluechip-Regular-Growth|98.7654|21-Feb-2025
119560|INF879O01100|INF879O01100|SBI Blue Chip-Direct-Growth|78.9012|21-Feb-2025
119561|INF879O01118|INF879O01118|SBI Blue Chip-Regular-Growth|65.4321|21-Feb-2025
119562|INF879O01126|INF879O01126|Axis Bluechip-Direct-Growth|56.7890|21-Feb-2025
119563|INF879O01134|INF879O01134|Axis Bluechip-Regular-Growth|47.2345|21-Feb-2025
119564|INF879O01142|INF879O01142|Mirae Asset Large Cap-Direct-Growth|34.5678|21-Feb-2025
119565|INF879O01159|INF879O01159|Mirae Asset Large Cap-Regular-Growth|29.8765|21-Feb-2025
119566|INF879O01167|INF879O01167|Nippon India Large Cap-Direct-Growth|78.1234|21-Feb-2025
119567|INF879O01175|INF879O01175|Nippon India Large Cap-Regular-Growth|62.5678|21-Feb-2025
"""


def test_parse_amfi_returns_valid_records():
    records = list(parse_amfi_nav(AMFI_FIXTURE))
    assert len(records) == 17, f"Expected 17 valid records, got {len(records)}"


def test_parse_amfi_skips_headers():
    records = list(parse_amfi_nav(AMFI_FIXTURE))
    # No record should have a scheme_name that looks like a category header
    for r in records:
        assert ';' not in r['scheme_name']
        assert 'Open Ended' not in r['scheme_name']


def test_parse_amfi_scheme_codes_are_strings_of_integers():
    records = list(parse_amfi_nav(AMFI_FIXTURE))
    for r in records:
        assert int(r['scheme_code']) > 0


def test_parse_amfi_nav_values_are_positive_floats():
    records = list(parse_amfi_nav(AMFI_FIXTURE))
    for r in records:
        assert isinstance(r['nav'], float)
        assert r['nav'] > 0


def test_parse_amfi_dates_are_date_objects():
    records = list(parse_amfi_nav(AMFI_FIXTURE))
    for r in records:
        assert isinstance(r['nav_date'], date)
        assert r['nav_date'] == date(2025, 2, 21)


def test_parse_amfi_skips_malformed_row():
    """Malformed row (wrong field count) should be silently skipped."""
    records = list(parse_amfi_nav(AMFI_FIXTURE))
    scheme_codes = {r['scheme_code'] for r in records}
    # The MALFORMED line should not appear
    assert 'MALFORMED_LINE_MISSING_FIELDS' not in scheme_codes
