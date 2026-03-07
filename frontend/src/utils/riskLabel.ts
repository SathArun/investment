export const RISK_LABELS: Record<number, string> = {
  1: 'Low',
  2: 'Low to Moderate',
  3: 'Moderate',
  4: 'Moderately High',
  5: 'High',
  6: 'Very High',
}

export const RISK_COLORS: Record<number, string> = {
  1: 'bg-green-500',
  2: 'bg-green-400',
  3: 'bg-yellow-400',
  4: 'bg-orange-400',
  5: 'bg-red-400',
  6: 'bg-red-600',
}

export function getRiskLabel(level: number): string {
  return RISK_LABELS[level] ?? 'Unknown'
}

export function getRiskColor(level: number): string {
  return RISK_COLORS[level] ?? 'bg-gray-400'
}

export function formatPct(value: number | null): string {
  if (value === null || value === undefined) return '—'
  return `${(value * 100).toFixed(2)}%`
}

export function formatCurrency(value: number | null): string {
  if (value === null || value === undefined) return '—'
  if (value >= 10000000) return `₹${(value / 10000000).toFixed(1)}Cr`
  if (value >= 100000) return `₹${(value / 100000).toFixed(1)}L`
  return `₹${value.toLocaleString('en-IN')}`
}
