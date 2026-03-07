"""Load reference JSON data into database tables."""
from __future__ import annotations
import json
import uuid
from datetime import date
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.base import engine, Base
from app.market_data.models import AssetClass
from app.analytics.models import TaxRule

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "reference"

_DATE_FIELDS = {"effective_from", "effective_until"}


def _parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    return date.fromisoformat(value)


def seed_asset_classes(session: Session) -> int:
    data = json.loads((DATA_DIR / "asset_classes.json").read_text())
    count = 0
    for row in data:
        existing = session.get(AssetClass, row["id"])
        if existing is None:
            obj = AssetClass(**row)
            session.add(obj)
            count += 1
    session.commit()
    return count


def seed_tax_rules(session: Session) -> int:
    data = json.loads((DATA_DIR / "tax_rules.json").read_text())
    count = 0
    for row in data:
        existing = session.get(TaxRule, row["id"])
        if existing is None:
            coerced = {k: v for k, v in row.items() if k != "notes"}
            for field in _DATE_FIELDS:
                if field in coerced:
                    coerced[field] = _parse_date(coerced[field])
            obj = TaxRule(**coerced)
            session.add(obj)
            count += 1
    session.commit()
    return count


def seed_test_advisor(session: Session) -> int:
    """Create a test advisor if none exists. Returns 1 if created, 0 otherwise."""
    from app.auth.models import Advisor
    from app.auth.service import hash_password

    existing = session.query(Advisor).filter(Advisor.email == "test@advisor.com").first()
    if existing is not None:
        return 0

    advisor = Advisor(
        id=str(uuid.uuid4()),
        email="test@advisor.com",
        password_hash=hash_password("TestPassword123!"),
        name="Test Advisor",
        is_active=True,
    )
    session.add(advisor)
    session.commit()
    return 1


def run_seed() -> None:
    from app.db.base import SessionLocal
    session = SessionLocal()
    try:
        ac_count = seed_asset_classes(session)
        tr_count = seed_tax_rules(session)
        adv_count = seed_test_advisor(session)
        print(f"Seeded: {ac_count} asset classes, {tr_count} tax rules, {adv_count} test advisors")
    finally:
        session.close()


if __name__ == "__main__":
    run_seed()
