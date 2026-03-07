import type { DataFreshness } from '@/types/product'

interface Props {
  freshness: DataFreshness
}

function isStale(timestamp: string | null): boolean {
  if (!timestamp) return true
  const diff = Date.now() - new Date(timestamp).getTime()
  return diff > 48 * 60 * 60 * 1000
}

export function DataFreshnessBar({ freshness }: Props) {
  const sources = [
    { label: 'AMFI', ts: freshness.amfi },
    { label: 'Equity', ts: freshness.equity },
    { label: 'NPS', ts: freshness.nps },
  ]
  return (
    <div className="flex gap-4 text-xs text-gray-500">
      {sources.map(({ label, ts }) => (
        <span key={label} className={isStale(ts) ? 'text-red-500' : 'text-green-600'}>
          {label}: {ts ? new Date(ts).toLocaleDateString('en-IN') : 'N/A'}
          {isStale(ts) && ' ⚠ stale'}
        </span>
      ))}
    </div>
  )
}
