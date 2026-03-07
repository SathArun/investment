"""Unit tests for NPS returns ingestion."""
from __future__ import annotations
from datetime import date

from app.jobs.ingest_nps import parse_nps_html, make_nps_ticker

# Simplified HTML fixture simulating NPSTRUST table structure
NPS_HTML_FIXTURE = """
<html><body>
<table>
<tr>
  <th>Pension Fund</th>
  <th>Scheme</th>
  <th>1 Year Returns</th>
  <th>3 Year Returns</th>
  <th>5 Year Returns</th>
</tr>
<tr>
  <td>SBI Pension Funds</td>
  <td>Equity</td>
  <td>18.52%</td>
  <td>14.23%</td>
  <td>12.78%</td>
</tr>
<tr>
  <td>SBI Pension Funds</td>
  <td>Government Bonds</td>
  <td>8.34%</td>
  <td>7.12%</td>
  <td>9.45%</td>
</tr>
<tr>
  <td>HDFC Pension Management</td>
  <td>Equity</td>
  <td>19.10%</td>
  <td>15.67%</td>
  <td>13.21%</td>
</tr>
<tr>
  <td>HDFC Pension Management</td>
  <td>Corporate Bonds</td>
  <td>9.20%</td>
  <td>8.45%</td>
  <td>N/A</td>
</tr>
</table>
</body></html>
"""


def test_make_nps_ticker():
    ticker = make_nps_ticker("SBI", "EQUITY", "1Y")
    assert ticker == "NPS_SBI_EQUITY_1Y"


def test_parse_nps_html_returns_records():
    records = parse_nps_html(NPS_HTML_FIXTURE, as_of_date=date(2025, 2, 21))
    assert len(records) > 0


def test_parse_nps_html_return_values_are_decimals():
    records = parse_nps_html(NPS_HTML_FIXTURE, as_of_date=date(2025, 2, 21))
    # Returns should be in decimal (e.g., 0.1852 not 18.52)
    for r in records:
        assert r["close_price"] < 1.0, f"Return not in decimal: {r['close_price']}"
        assert r["close_price"] > 0


def test_parse_nps_html_uses_given_date():
    test_date = date(2025, 1, 15)
    records = parse_nps_html(NPS_HTML_FIXTURE, as_of_date=test_date)
    for r in records:
        assert r["price_date"] == test_date


def test_parse_nps_html_sbi_equity_present():
    records = parse_nps_html(NPS_HTML_FIXTURE, as_of_date=date(2025, 2, 21))
    tickers = {r["ticker"] for r in records}
    assert "NPS_SBI_EQUITY_1Y" in tickers or any("SBI" in t and "EQUITY" in t for t in tickers)
