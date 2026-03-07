"""SEBI-compliant risk profiler questionnaire."""
from __future__ import annotations

QUESTIONS = [
    # --- Age (2 questions) ---
    {
        "id": "q01",
        "text": "What is your current age?",
        "category": "age",
        "options": [
            {"value": "under_35", "label": "Under 35", "score": 5},
            {"value": "35_50", "label": "35 to 50", "score": 3},
            {"value": "50_60", "label": "50 to 60", "score": 2},
            {"value": "above_60", "label": "Above 60", "score": 1},
        ],
    },
    {
        "id": "q02",
        "text": "At what age do you plan to retire (or have you already retired)?",
        "category": "age",
        "options": [
            {"value": "retire_above_60", "label": "Above 60", "score": 5},
            {"value": "retire_55_60", "label": "55 to 60", "score": 3},
            {"value": "retire_50_55", "label": "50 to 55", "score": 2},
            {"value": "retire_below_50", "label": "Below 50 or already retired", "score": 1},
        ],
    },
    # --- Income (3 questions) ---
    {
        "id": "q03",
        "text": "How would you describe the stability of your primary income source?",
        "category": "income",
        "options": [
            {"value": "very_stable", "label": "Very stable (government/large corporate salaried)", "score": 5},
            {"value": "stable", "label": "Stable (private sector salaried)", "score": 4},
            {"value": "variable", "label": "Variable (self-employed / freelance)", "score": 2},
            {"value": "irregular", "label": "Irregular or no current income", "score": 1},
        ],
    },
    {
        "id": "q04",
        "text": "What is your approximate annual household income (INR)?",
        "category": "income",
        "options": [
            {"value": "above_25L", "label": "Above ₹25 lakhs", "score": 5},
            {"value": "10_25L", "label": "₹10 lakhs to ₹25 lakhs", "score": 4},
            {"value": "5_10L", "label": "₹5 lakhs to ₹10 lakhs", "score": 3},
            {"value": "below_5L", "label": "Below ₹5 lakhs", "score": 1},
        ],
    },
    {
        "id": "q05",
        "text": "How many dependents rely on your income?",
        "category": "income",
        "options": [
            {"value": "none", "label": "None", "score": 5},
            {"value": "one_two", "label": "1 to 2", "score": 3},
            {"value": "three_four", "label": "3 to 4", "score": 2},
            {"value": "five_plus", "label": "5 or more", "score": 1},
        ],
    },
    # --- Assets (2 questions) ---
    {
        "id": "q06",
        "text": "What percentage of your savings is currently invested in market-linked instruments (equities, equity mutual funds, etc.)?",
        "category": "assets",
        "options": [
            {"value": "above_60pct", "label": "More than 60%", "score": 5},
            {"value": "30_60pct", "label": "30% to 60%", "score": 4},
            {"value": "10_30pct", "label": "10% to 30%", "score": 2},
            {"value": "below_10pct", "label": "Less than 10% (mostly FDs / savings)", "score": 1},
        ],
    },
    {
        "id": "q07",
        "text": "Do you have an emergency fund covering at least 6 months of expenses?",
        "category": "assets",
        "options": [
            {"value": "yes_12plus", "label": "Yes, covering more than 12 months", "score": 5},
            {"value": "yes_6_12", "label": "Yes, covering 6 to 12 months", "score": 4},
            {"value": "partial", "label": "Partial — covers 1 to 5 months", "score": 2},
            {"value": "no", "label": "No emergency fund", "score": 1},
        ],
    },
    # --- Investment Objective (3 questions) ---
    {
        "id": "q08",
        "text": "What is your primary investment objective?",
        "category": "objective",
        "options": [
            {"value": "aggressive_growth", "label": "Aggressive wealth creation — I can accept high volatility", "score": 5},
            {"value": "growth", "label": "Long-term growth with moderate volatility", "score": 4},
            {"value": "balanced", "label": "Balanced growth and capital protection", "score": 3},
            {"value": "capital_preservation", "label": "Capital preservation — I cannot afford losses", "score": 1},
        ],
    },
    {
        "id": "q09",
        "text": "What annual return do you realistically expect from your investments?",
        "category": "objective",
        "options": [
            {"value": "above_15pct", "label": "Above 15% (equity-like returns)", "score": 5},
            {"value": "10_15pct", "label": "10% to 15%", "score": 4},
            {"value": "6_10pct", "label": "6% to 10%", "score": 3},
            {"value": "below_6pct", "label": "Below 6% (FD-like returns)", "score": 1},
        ],
    },
    {
        "id": "q10",
        "text": "What is the maximum loss in a year you could tolerate without changing your investment strategy?",
        "category": "objective",
        "options": [
            {"value": "above_30pct", "label": "More than 30%", "score": 5},
            {"value": "15_30pct", "label": "15% to 30%", "score": 4},
            {"value": "5_15pct", "label": "5% to 15%", "score": 2},
            {"value": "no_loss", "label": "I cannot tolerate any loss", "score": 1},
        ],
    },
    # --- Investment Horizon (3 questions) ---
    {
        "id": "q11",
        "text": "How long do you intend to stay invested before you need the money?",
        "category": "horizon",
        "options": [
            {"value": "above_10yr", "label": "More than 10 years", "score": 5},
            {"value": "7_10yr", "label": "7 to 10 years", "score": 4},
            {"value": "3_7yr", "label": "3 to 7 years", "score": 3},
            {"value": "below_3yr", "label": "Less than 3 years", "score": 1},
        ],
    },
    {
        "id": "q12",
        "text": "How likely are you to need a significant portion of this investment before the planned horizon?",
        "category": "horizon",
        "options": [
            {"value": "very_unlikely", "label": "Very unlikely — I have separate funds for emergencies", "score": 5},
            {"value": "unlikely", "label": "Unlikely but possible", "score": 3},
            {"value": "possible", "label": "Somewhat likely", "score": 2},
            {"value": "likely", "label": "Likely — I may need it within 1 to 2 years", "score": 1},
        ],
    },
    {
        "id": "q13",
        "text": "Are you investing for a specific goal (home, retirement, education)?",
        "category": "horizon",
        "options": [
            {"value": "retirement_longterm", "label": "Retirement — more than 10 years away", "score": 5},
            {"value": "goal_medium", "label": "Specific goal 5 to 10 years away", "score": 3},
            {"value": "goal_short", "label": "Specific goal within 5 years", "score": 2},
            {"value": "no_goal", "label": "No specific goal — may need funds anytime", "score": 1},
        ],
    },
    # --- Behavioral Risk (3 questions) ---
    {
        "id": "q14",
        "text": "If your portfolio dropped by 20% in three months, what would you do?",
        "category": "behavioral",
        "options": [
            {"value": "buy_more", "label": "Buy more — I see it as an opportunity", "score": 5},
            {"value": "hold", "label": "Hold and wait for recovery", "score": 4},
            {"value": "sell_some", "label": "Sell a portion to reduce exposure", "score": 2},
            {"value": "sell_all", "label": "Sell everything to avoid further losses", "score": 1},
        ],
    },
    {
        "id": "q15",
        "text": "What is your previous investment experience?",
        "category": "behavioral",
        "options": [
            {"value": "extensive", "label": "Extensive — I have traded equities, derivatives, or managed a portfolio for 5+ years", "score": 5},
            {"value": "moderate", "label": "Moderate — I have invested in mutual funds or equities for 2 to 5 years", "score": 4},
            {"value": "limited", "label": "Limited — I have invested for less than 2 years", "score": 2},
            {"value": "none", "label": "None — I am a first-time investor", "score": 1},
        ],
    },
    {
        "id": "q16",
        "text": "Which portfolio scenario would you feel most comfortable with over a 5-year period?",
        "category": "behavioral",
        "options": [
            {"value": "high_growth_high_risk", "label": "Potential gain of 80% with possible loss of 40%", "score": 5},
            {"value": "growth_moderate_risk", "label": "Potential gain of 50% with possible loss of 20%", "score": 4},
            {"value": "moderate_low_risk", "label": "Potential gain of 25% with possible loss of 8%", "score": 2},
            {"value": "low_gain_no_loss", "label": "Potential gain of 10% with near-zero loss", "score": 1},
        ],
    },
    # --- Liquidity (2 questions) ---
    {
        "id": "q17",
        "text": "Do you anticipate needing a large lump-sum (more than 25% of your portfolio) within the next 12 months?",
        "category": "liquidity",
        "options": [
            {"value": "no", "label": "No — no major expense planned", "score": 5},
            {"value": "small", "label": "Small expense — less than 10% of portfolio", "score": 4},
            {"value": "medium", "label": "Medium expense — 10% to 25% of portfolio", "score": 2},
            {"value": "large", "label": "Yes — more than 25% of portfolio", "score": 1},
        ],
    },
    {
        "id": "q18",
        "text": "How many months of living expenses does your current liquid savings (savings account / liquid funds) cover?",
        "category": "liquidity",
        "options": [
            {"value": "above_12", "label": "More than 12 months", "score": 5},
            {"value": "6_12", "label": "6 to 12 months", "score": 4},
            {"value": "3_6", "label": "3 to 6 months", "score": 2},
            {"value": "below_3", "label": "Less than 3 months", "score": 1},
        ],
    },
]


def get_questions() -> list[dict]:
    """Return the full SEBI risk profiler questionnaire."""
    return QUESTIONS
