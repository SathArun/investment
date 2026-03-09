import { useFilterStore } from '@/store/filterStore'
import { useUIStore } from '@/store/uiStore'

const TAX_LABELS: Record<string, string> = {
  '0': '0% (No Tax)',
  '0.05': '5%',
  '0.1': '10%',
  '0.2': '20%',
  '0.3': '30%',
}

const HORIZON_LABELS: Record<string, string> = {
  short: 'Short (< 3Y)',
  medium: 'Medium (3–7Y)',
  long: 'Long (7Y+)',
}

export function FilterSummary() {
  const taxBracket = useFilterStore((s) => s.taxBracket)
  const timeHorizon = useFilterStore((s) => s.timeHorizon)
  const riskFilter = useFilterStore((s) => s.riskFilter)
  const setClientView = useUIStore((s) => s.setClientView)

  const taxLabel = TAX_LABELS[String(taxBracket)] ?? '—'
  const horizonLabel = HORIZON_LABELS[timeHorizon] ?? '—'
  const riskLabel = riskFilter ?? '—'

  return (
    <div className="flex items-center gap-3 text-sm text-gray-600">
      <span>
        Filtered:{' '}
        <span className="font-medium text-gray-800">{taxLabel}</span>
        {' · '}
        <span className="font-medium text-gray-800">{horizonLabel}</span>
        {' · '}
        <span className="font-medium text-gray-800">{riskLabel}</span>
      </span>
      <button
        onClick={() => setClientView(false)}
        className="text-blue-600 hover:underline text-sm"
      >
        Change filters
      </button>
    </div>
  )
}
