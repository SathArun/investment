/**
 * Simulates monthly withdrawals from a corpus.
 * Returns array of remaining balances at end of each year.
 * Stops when corpus reaches 0.
 */
export interface WithdrawalSimResult {
  yearlyBalances: number[]   // remaining balance at end of each year
  yearsLasted: number        // how many years corpus lasts (0 if already exhausted)
  exhausted: boolean
}

export function simulateWithdrawal(
  initialCorpus: number,
  monthlyWithdrawal: number,
  annualReturn: number,   // decimal, e.g. 0.08
  maxYears: number = 50,
): WithdrawalSimResult {
  const monthlyReturn = annualReturn / 12
  let corpus = initialCorpus
  const yearlyBalances: number[] = []
  let exhaustedYear = -1

  for (let yr = 1; yr <= maxYears; yr++) {
    for (let m = 0; m < 12; m++) {
      corpus = corpus * (1 + monthlyReturn) - monthlyWithdrawal
      if (corpus <= 0) {
        corpus = 0
        if (exhaustedYear === -1) exhaustedYear = yr
        break
      }
    }
    yearlyBalances.push(Math.round(corpus))
    if (corpus === 0) break
  }

  return {
    yearlyBalances,
    yearsLasted: exhaustedYear === -1 ? maxYears : exhaustedYear,
    exhausted: exhaustedYear !== -1,
  }
}
