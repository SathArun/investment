/**
 * Future value of SIP with annual step-up
 * r = annual return rate (decimal), g = annual step-up (decimal), n = years, sip = monthly SIP
 */
export function fvSipWithStepup(
  sip: number,
  annualReturn: number,
  annualStepup: number,
  years: number,
): number {
  const r = annualReturn / 12 // monthly return
  const g = annualStepup / 12 // monthly step-up

  if (Math.abs(r - g) < 1e-10) {
    // r ≈ g: simplified formula
    const months = years * 12
    return sip * months * Math.pow(1 + r, months / 2)
  }

  // Step-up FV: sum over each year
  let total = 0
  for (let yr = 0; yr < years; yr++) {
    const sipThisYear = sip * Math.pow(1 + annualStepup, yr)
    const monthsRemaining = (years - yr) * 12
    // FV of level SIP for months remaining
    total += (sipThisYear * (Math.pow(1 + r, monthsRemaining) - 1)) / r
  }
  return total
}

/**
 * Corpus projection series: list of yearly balances over `years` years
 * Includes both existing corpus growth and SIP accumulation
 */
export function corpusProjection(
  currentCorpus: number,
  monthlySip: number,
  annualStepup: number,
  annualReturn: number,
  years: number,
): number[] {
  const series: number[] = []
  let corpus = currentCorpus
  let sip = monthlySip

  for (let yr = 1; yr <= years; yr++) {
    corpus = corpus * (1 + annualReturn) + sip * 12 * (1 + annualReturn / 2)
    sip = sip * (1 + annualStepup)
    series.push(Math.round(corpus))
  }
  return series
}
