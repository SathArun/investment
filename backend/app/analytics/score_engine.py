from __future__ import annotations
from typing import Optional
import scipy.stats


def normalize_to_percentile(value: Optional[float], universe: list[float]) -> float:
    """
    Compute percentile rank of value within universe using scipy.
    Returns 0.0 if value is None or universe is empty.
    """
    if value is None or not universe:
        return 0.0
    return float(scipy.stats.percentileofscore(universe, value, kind='rank'))


def compute_liquidity_score(lock_in_days: int) -> float:
    """
    Convert lock-in days to a 0-100 liquidity score (higher = more liquid).
    Per SDD lookup table:
    - 0 days: 100 (same-day liquid)
    - <= 1 day: 90 (T+1)
    - <= 3 days: 75 (T+2-3)
    - <= 365 days: 50 (< 1 year)
    - -1: 10 (NPS until age 60)
    - >= 5475: 20 (PPF 15Y)
    - else: MAX(10, 70 - (lock_in_days/365)*10)
    """
    if lock_in_days == 0:
        return 100.0
    if lock_in_days == -1:
        return 10.0
    if lock_in_days <= 1:
        return 90.0
    if lock_in_days <= 3:
        return 75.0
    if lock_in_days <= 365:
        return 50.0
    if lock_in_days >= 5475:
        return 20.0
    return max(10.0, 70.0 - (lock_in_days / 365) * 10.0)


def compute_goal_fit(sebi_risk_level: int, time_horizon: str) -> float:
    """
    Compute goal-fit alignment score based on SEBI risk level and time horizon.
    Per SDD alignment matrix.
    """
    if time_horizon == 'short':
        if sebi_risk_level <= 2:
            return 100.0
        if sebi_risk_level == 3:
            return 70.0
        return 30.0  # sebi_risk_level >= 4
    if time_horizon == 'medium':
        if sebi_risk_level <= 2:
            return 60.0
        if sebi_risk_level in (3, 4):
            return 100.0
        return 50.0  # sebi_risk_level >= 5
    if time_horizon == 'long':
        if sebi_risk_level <= 2:
            return 40.0
        if sebi_risk_level == 3:
            return 70.0
        return 100.0  # sebi_risk_level >= 4
    return 50.0  # fallback


# Score weights per SDD
WEIGHTS = {
    'risk_adjusted': 0.30,
    'tax_yield': 0.25,
    'liquidity': 0.15,
    'expense': 0.10,
    'consistency': 0.10,
    'goal_fit': 0.10,
}


def compute_advisor_score(
    sharpe: Optional[float],
    sortino: Optional[float],
    post_tax_return_3y: Optional[float],
    std_dev_3y: Optional[float],
    expense_ratio: Optional[float],
    lock_in_days: int,
    sebi_risk_level: int,
    time_horizon: str,
    # Universe vectors (all products in this bracket+horizon iteration)
    sharpe_universe: list[float],
    sortino_universe: list[float],
    post_tax_universe: list[float],
    std_dev_universe: list[float],
    expense_universe: list[float],
) -> dict:
    """
    Compute the 6 sub-scores and composite advisor_score.

    Returns dict with: score_total, score_risk_adjusted, score_tax_yield,
    score_liquidity, score_expense, score_consistency, score_goal_fit
    """
    # 1. Risk-adjusted: average of Sharpe and Sortino percentiles
    sharpe_pct = normalize_to_percentile(sharpe, sharpe_universe)
    sortino_pct = normalize_to_percentile(sortino, sortino_universe)
    score_risk_adjusted = 0.5 * sharpe_pct + 0.5 * sortino_pct

    # 2. Tax yield: percentile of post-tax return
    score_tax_yield = normalize_to_percentile(post_tax_return_3y, post_tax_universe)

    # 3. Liquidity: direct lookup (not percentile-normalized)
    score_liquidity = compute_liquidity_score(lock_in_days)

    # 4. Expense: lower cost -> higher score (inverse percentile)
    if expense_ratio is not None and expense_universe:
        expense_pct = normalize_to_percentile(expense_ratio, expense_universe)
        score_expense = 100.0 - expense_pct  # invert
    else:
        score_expense = 50.0  # neutral for products with no expense data

    # 5. Consistency: lower std_dev -> higher score (inverse percentile)
    if std_dev_3y is not None and std_dev_universe:
        std_pct = normalize_to_percentile(std_dev_3y, std_dev_universe)
        score_consistency = 100.0 - std_pct  # invert: low variance -> high consistency
    else:
        score_consistency = 100.0  # zero-variance products (PPF) get perfect consistency

    # 6. Goal fit: alignment matrix
    score_goal_fit = compute_goal_fit(sebi_risk_level, time_horizon)

    # Composite weighted sum
    score_total = (
        score_risk_adjusted * WEIGHTS['risk_adjusted'] +
        score_tax_yield * WEIGHTS['tax_yield'] +
        score_liquidity * WEIGHTS['liquidity'] +
        score_expense * WEIGHTS['expense'] +
        score_consistency * WEIGHTS['consistency'] +
        score_goal_fit * WEIGHTS['goal_fit']
    )

    return {
        'score_total': round(score_total, 2),
        'score_risk_adjusted': round(score_risk_adjusted, 2),
        'score_tax_yield': round(score_tax_yield, 2),
        'score_liquidity': round(score_liquidity, 2),
        'score_expense': round(score_expense, 2),
        'score_consistency': round(score_consistency, 2),
        'score_goal_fit': round(score_goal_fit, 2),
    }
