from __future__ import annotations
import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])

_STRESS_SCENARIOS_PATH = Path(__file__).parent.parent.parent / "data" / "reference" / "stress_scenarios.json"


@router.get("/stress-test")
def get_stress_scenarios():
    with open(_STRESS_SCENARIOS_PATH) as f:
        return json.load(f)
