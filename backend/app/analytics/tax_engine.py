from __future__ import annotations
import functools
import json
import re
from datetime import date
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger()

TAX_RULES_PATH = Path(__file__).parent.parent.parent / "data" / "reference" / "tax_rules.json"
_HOLDING_SHORT_MONTHS = 12  # < 12 months = STCG for equity


def _glob_to_regex(pattern: str) -> str:
    """Convert a simple glob pattern (using * as wildcard) to a regex pattern."""
    # Escape regex special chars except *, then replace * with .*
    escaped = re.escape(pattern).replace(r"\*", ".*")
    return escaped


@functools.lru_cache(maxsize=4)
def _load_tax_rules_cached(as_of_date: date) -> list[dict]:
    rules = json.loads(TAX_RULES_PATH.read_text())
    active = []
    for rule in rules:
        eff_from = date.fromisoformat(rule["effective_from"])
        eff_until_str = rule.get("effective_until")
        eff_until = date.fromisoformat(eff_until_str) if eff_until_str else date(9999, 12, 31)
        if eff_from <= as_of_date <= eff_until:
            active.append(rule)
    return active


def load_tax_rules(as_of_date: Optional[date] = None) -> list[dict]:
    """Load tax rules from JSON, cached per date. Disk read only once per date per process."""
    if as_of_date is None:
        as_of_date = date.today()
    return list(_load_tax_rules_cached(as_of_date))


def find_applicable_rule(
    asset_class_id: str,
    holding_years: float,
    rules: Optional[list[dict]] = None
) -> Optional[dict]:
    """
    Find the best-matching tax rule for asset_class_id + holding period.
    Matches by asset_class_pattern (glob with * wildcard, matched via regex)
    and holding_period_type.
    """
    if rules is None:
        rules = load_tax_rules()
    holding_months = holding_years * 12

    matching = []
    for rule in rules:
        glob_pattern = rule.get("asset_class_pattern", "")
        regex_pattern = _glob_to_regex(glob_pattern)
        if not re.fullmatch(regex_pattern, asset_class_id, re.IGNORECASE):
            continue

        htype = rule.get("holding_period_type", "any")
        threshold = rule.get("holding_period_months") or 12

        if htype in ("all", "any"):
            matching.append(rule)
        elif htype == "short" and holding_months < threshold:
            matching.append(rule)
        elif htype == "long" and holding_months >= threshold:
            matching.append(rule)
        elif htype == "maturity" and holding_months >= threshold:
            # SGB maturity: held >= 96 months (8 years)
            matching.append(rule)
        elif htype == "premature" and holding_months < threshold:
            # SGB premature exit: held < 96 months
            matching.append(rule)

    if not matching:
        return None

    # Prefer more specific rules:
    #   1. Non-"any"/"all" holding_period_type over "any"/"all"
    #   2. Longer asset_class_pattern (more specific) wins
    def _sort_key(r: dict):
        is_generic_holding = r.get("holding_period_type", "any") in ("all", "any")
        pattern_len = len(r.get("asset_class_pattern", ""))
        return (is_generic_holding, -pattern_len)

    matching.sort(key=_sort_key)
    return matching[0]


def compute_post_tax_cagr(
    asset_class_id: str,
    pre_tax_cagr: float,
    investment_inr: float,
    tax_bracket: float,
    holding_years: float,
) -> dict:
    """
    Compute post-tax CAGR for an investment.
    Returns dict with: post_tax_cagr, rule_id, tax_description, effective_tax_rate
    """
    rules = load_tax_rules()
    rule = find_applicable_rule(asset_class_id, holding_years, rules)

    if rule is None:
        logger.warning("no_tax_rule_found", asset_class_id=asset_class_id)
        return {
            "post_tax_cagr": pre_tax_cagr,
            "rule_id": "none",
            "tax_description": "No rule found — pre-tax returned",
            "effective_tax_rate": 0.0,
        }

    special_rule = rule.get("special_rule")

    # EEE products (PPF, NPS partial, etc.)
    if special_rule in ("ppf_eee", "eee", "tax_free"):
        return {
            "post_tax_cagr": pre_tax_cagr,
            "rule_id": rule["id"],
            "tax_description": "Tax Free (EEE)",
            "effective_tax_rate": 0.0,
        }

    # SGB maturity (8Y hold) — tax-free
    if special_rule == "sgb_maturity_tax_free":
        threshold_months = rule.get("holding_period_months") or 96
        if holding_years * 12 >= threshold_months:
            return {
                "post_tax_cagr": pre_tax_cagr,
                "rule_id": rule["id"],
                "tax_description": "SGB Maturity — Tax Free",
                "effective_tax_rate": 0.0,
            }

    # Compute gross corpus
    gross_corpus = investment_inr * (1 + pre_tax_cagr) ** holding_years
    gain = gross_corpus - investment_inr

    if gain <= 0:
        return {
            "post_tax_cagr": pre_tax_cagr,
            "rule_id": rule.get("id", "none"),
            "tax_description": "No gain",
            "effective_tax_rate": 0.0,
        }

    # Determine tax rate from tax_rate_expression
    tax_rate_expr = rule.get("tax_rate_expression", "")
    if tax_rate_expr == "slab_rate":
        tax_rate = tax_bracket
    else:
        try:
            tax_rate = float(tax_rate_expr)
        except (ValueError, TypeError):
            tax_rate = rule.get("tax_rate", 0.0)

    # Apply annual exemption (Rs 1.25L for equity LTCG)
    annual_exemption = rule.get("annual_exemption_inr") or 0
    taxable_gain = max(0, gain - annual_exemption)

    tax_paid = taxable_gain * tax_rate
    net_corpus = gross_corpus - tax_paid
    post_tax_cagr = (net_corpus / investment_inr) ** (1.0 / holding_years) - 1
    effective_rate = tax_paid / gain if gain > 0 else 0.0

    return {
        "post_tax_cagr": float(post_tax_cagr),
        "rule_id": rule.get("id", "unknown"),
        "tax_description": rule.get("description", ""),
        "effective_tax_rate": float(effective_rate),
        "annual_exemption_used": float(min(gain, annual_exemption)) if annual_exemption > 0 else None,
    }
