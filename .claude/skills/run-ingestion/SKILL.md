---
name: run-ingestion
description: Manually run a background ingestion or compute job (AMFI, equity, NPS, mfapi, metrics, scores)
disable-model-invocation: true
---

Show this menu and ask which job to run:

1. `ingest_amfi`     - AMFI mutual fund NAVs (daily 23:30)
2. `ingest_equity`   - NSE/BSE index prices via yfinance (weekdays 16:30)
3. `ingest_nps`      - NPS returns (Mondays 07:00)
4. `ingest_mfapi`    - Historical NAV backfill (Sundays 02:00)
5. `compute_metrics` - CAGR, Sharpe, Sortino, max drawdown (daily 01:00)
6. `compute_scores`  - 6-dimensional scores ~30k combinations (daily 00:00)

Run the chosen job:

    cd /c/Arun/investment/backend && python -m app.jobs.<chosen_job>

Show the last 30 lines of output. Report:
- Number of records ingested/updated
- Any errors or warnings
- Time taken if available
