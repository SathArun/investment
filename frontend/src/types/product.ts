export interface ScoreBreakdown {
  risk_adjusted: number
  tax_yield: number
  liquidity: number
  expense: number
  consistency: number
  goal_fit: number
}

export interface ProductRow {
  id: number
  name: string
  asset_class: string
  sebi_risk_level: number
  cagr_1y: number | null
  cagr_3y: number | null
  cagr_5y: number | null
  cagr_10y: number | null
  post_tax_return_1y: number | null
  post_tax_return_3y: number | null
  post_tax_return_5y: number | null
  std_dev_3y: number | null
  sharpe_3y: number | null
  max_drawdown_5y: number | null
  expense_ratio: number | null
  min_investment_inr: number | null
  liquidity_label: string | null
  advisor_score: number
  score_breakdown: ScoreBreakdown
}

export interface DataFreshness {
  amfi: string | null
  equity: string | null
  nps: string | null
}

export type TaxBracket = 0 | 0.05 | 0.1 | 0.2 | 0.3
export type TimeHorizon = 'short' | 'medium' | 'long'
export type RiskFilter = 'All' | 'Conservative' | 'Moderate' | 'Aggressive'
export type SortDir = 'asc' | 'desc'
