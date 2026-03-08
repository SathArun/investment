"""yfinance NSE/BSE index and equity data ingestion."""
from __future__ import annotations
import json
import time
from datetime import date
from pathlib import Path

import structlog
import yfinance as yf

from app.db.base import SessionLocal
from app.market_data.models import IndexHistory

logger = structlog.get_logger()

TICKERS_FILE = Path(__file__).parent.parent.parent / "data" / "reference" / "index_tickers.json"


def load_ticker_config() -> list[dict]:
    return json.loads(TICKERS_FILE.read_text())


def fetch_index_history(ticker: str, period: str = "10y") -> list[dict]:
    """Fetch historical price data for a ticker using yfinance."""
    try:
        data = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        if data.empty:
            logger.warning("yfinance_empty", ticker=ticker)
            return []

        # yfinance >= 1.0 returns a MultiIndex on columns; flatten to single-level
        import pandas as pd
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        records = []
        for idx, row in data.iterrows():
            price_date = idx.date() if hasattr(idx, 'date') else idx
            close_val = row.get('Close')
            if close_val is None:
                continue
            try:
                close = float(close_val)
            except (TypeError, ValueError):
                continue
            if close > 0:
                records.append({"ticker": ticker, "price_date": price_date, "close_price": close})
        return records
    except Exception as e:
        logger.error("yfinance_fetch_error", ticker=ticker, error=str(e))
        return []


def upsert_index_history(ticker: str, records: list[dict], session) -> tuple[int, int]:
    """Upsert index history records. Returns (inserted, skipped)."""
    inserted = 0
    skipped = 0
    for record in records:
        existing = session.get(IndexHistory, (record["ticker"], record["price_date"]))
        if existing is not None:
            skipped += 1
            continue
        row = IndexHistory(
            ticker=record["ticker"],
            price_date=record["price_date"],
            close_price=record["close_price"],
        )
        session.add(row)
        inserted += 1
    session.commit()
    return inserted, skipped


def run() -> int:
    """Main entry point: fetch and store all configured index tickers. Returns total inserted rows."""
    ticker_configs = load_ticker_config()
    logger.info("equity_job_start", ticker_count=len(ticker_configs))

    with SessionLocal() as session:
        total_inserted = 0
        for config in ticker_configs:
            ticker = config["ticker"]
            try:
                records = fetch_index_history(ticker)
                if records:
                    inserted, skipped = upsert_index_history(ticker, records, session)
                    logger.info("equity_ticker_done", ticker=ticker, inserted=inserted, skipped=skipped)
                    total_inserted += inserted
                else:
                    logger.warning("equity_ticker_no_data", ticker=ticker)
                time.sleep(0.5)  # Polite rate limiting
            except Exception as e:
                logger.error("equity_ticker_error", ticker=ticker, error=str(e))
                # Continue with next ticker — don't abort
                continue

    logger.info("equity_job_complete", total_inserted=total_inserted)
    return total_inserted


if __name__ == "__main__":
    run()
