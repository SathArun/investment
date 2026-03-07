"""
Seed mutual fund NAV history from mfapi.in for popular funds.
Run from backend directory: python scripts/seed_nav_data.py
"""
from __future__ import annotations
import sys
import time
from datetime import datetime

import requests

sys.path.insert(0, ".")
from app.db.session import SessionLocal
from app.market_data.models import MutualFund, NavHistory

MFAPI_BASE = "https://api.mfapi.in/mf"

# scheme_code, scheme_name, asset_class_id, amfi_category, amc_name, direct_plan
FUNDS = [
    ("119598", "SBI Bluechip Fund - Direct Plan - Growth", "eq_largecap", "Large Cap Fund", "SBI Funds Management", True),
    ("118834", "Mirae Asset Large Cap Fund - Direct Plan - Growth", "eq_largecap", "Large Cap Fund", "Mirae Asset", True),
    ("118989", "HDFC Mid-Cap Opportunities Fund - Direct Plan - Growth", "eq_midcap", "Mid Cap Fund", "HDFC AMC", True),
    ("118778", "Nippon India Small Cap Fund - Direct Plan - Growth", "eq_smallcap", "Small Cap Fund", "Nippon India", True),
    ("122639", "Parag Parikh Flexi Cap Fund - Direct Plan - Growth", "eq_flexicap", "Flexi Cap Fund", "PPFAS", True),
    ("120503", "Axis ELSS Tax Saver Fund - Direct Plan - Growth", "eq_elss", "ELSS", "Axis AMC", True),
    ("118825", "Nippon India Liquid Fund - Direct Plan - Growth", "debt_liquid", "Liquid Fund", "Nippon India", True),
    ("118990", "HDFC Short Term Debt Fund - Direct Plan - Growth", "debt_shortterm", "Short Duration Fund", "HDFC AMC", True),
    ("119215", "HDFC Corporate Bond Fund - Direct Plan - Growth", "debt_corporate", "Corporate Bond Fund", "HDFC AMC", True),
    ("120716", "Mirae Asset Nifty 50 ETF", "eq_index", "Index Fund", "Mirae Asset", True),
]


def fetch_nav_history(scheme_code: str) -> list[dict]:
    url = f"{MFAPI_BASE}/{scheme_code}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


def run():
    session = SessionLocal()
    try:
        for scheme_code, scheme_name, asset_class_id, amfi_cat, amc, direct in FUNDS:
            # Upsert fund record
            fund = session.get(MutualFund, scheme_code)
            if fund is None:
                fund = MutualFund(
                    scheme_code=scheme_code,
                    scheme_name=scheme_name,
                    asset_class_id=asset_class_id,
                    amfi_category=amfi_cat,
                    amc_name=amc,
                    direct_plan=direct,
                    is_active=True,
                )
                session.add(fund)
                session.commit()
                print(f"  Added fund: {scheme_code} {scheme_name}")
            else:
                print(f"  Fund exists: {scheme_code}")

            # Fetch and insert historical NAV
            print(f"  Fetching NAV history for {scheme_code}...", end=" ", flush=True)
            try:
                records = fetch_nav_history(scheme_code)
            except Exception as e:
                print(f"FAILED ({e})")
                continue

            inserted = 0
            skipped = 0
            for r in records:
                try:
                    nav_date = datetime.strptime(r["date"], "%d-%m-%Y").date()
                    nav_val = float(r["nav"])
                except (ValueError, KeyError):
                    skipped += 1
                    continue

                existing = session.get(NavHistory, (scheme_code, nav_date))
                if existing:
                    skipped += 1
                    continue

                session.add(NavHistory(scheme_code=scheme_code, nav_date=nav_date, nav=nav_val))
                inserted += 1

                if inserted % 500 == 0:
                    session.commit()

            session.commit()
            print(f"inserted={inserted} skipped={skipped} total={len(records)}")
            time.sleep(0.5)  # polite rate limit

        print("\nDone. Now run: python -m app.jobs.compute_metrics")
    finally:
        session.close()


if __name__ == "__main__":
    run()
