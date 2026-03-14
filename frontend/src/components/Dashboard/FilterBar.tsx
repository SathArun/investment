import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useFilterStore } from '@/store/filterStore'
import { useDashboardStore } from '@/store/dashboardStore'
import type { TaxBracket, TimeHorizon, RiskFilter } from '@/types/product'

interface SelectOption {
  label: string
  value: string
}

interface SimpleSelectProps {
  label: string
  value: string
  options: SelectOption[]
  onValueChange: (value: string) => void
}

function SimpleSelect({ label, value, options, onValueChange }: SimpleSelectProps) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-muted-foreground">{label}</label>
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger className="min-w-[160px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>
              {opt.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}

const TAX_BRACKET_OPTIONS: SelectOption[] = [
  { label: '0% (No Tax)', value: '0' },
  { label: '5%', value: '0.05' },
  { label: '10%', value: '0.1' },
  { label: '20%', value: '0.2' },
  { label: '30%', value: '0.3' },
]

const TIME_HORIZON_OPTIONS: SelectOption[] = [
  { label: 'Short (< 3Y)', value: 'short' },
  { label: 'Medium (3–7Y)', value: 'medium' },
  { label: 'Long (7Y+)', value: 'long' },
]

const RISK_FILTER_OPTIONS: SelectOption[] = [
  { label: 'All', value: 'All' },
  { label: 'Conservative', value: 'Conservative' },
  { label: 'Moderate', value: 'Moderate' },
  { label: 'Aggressive', value: 'Aggressive' },
]

export function FilterBar() {
  const { taxBracket, timeHorizon, riskFilter, setTaxBracket, setTimeHorizon, setRiskFilter } =
    useFilterStore()
  const { fetchProducts } = useDashboardStore()

  function handleTaxBracketChange(value: string) {
    const parsed = parseFloat(value) as TaxBracket
    setTaxBracket(parsed)
    fetchProducts(parsed, timeHorizon, riskFilter)
  }

  function handleTimeHorizonChange(value: string) {
    const horizon = value as TimeHorizon
    setTimeHorizon(horizon)
    fetchProducts(taxBracket, horizon, riskFilter)
  }

  function handleRiskFilterChange(value: string) {
    const risk = value as RiskFilter
    setRiskFilter(risk)
    fetchProducts(taxBracket, timeHorizon, risk)
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-end gap-4">
        <SimpleSelect
          label="Tax Bracket"
          value={String(taxBracket)}
          options={TAX_BRACKET_OPTIONS}
          onValueChange={handleTaxBracketChange}
        />
        <SimpleSelect
          label="Time Horizon"
          value={timeHorizon}
          options={TIME_HORIZON_OPTIONS}
          onValueChange={handleTimeHorizonChange}
        />
        <SimpleSelect
          label="Risk Filter"
          value={riskFilter}
          options={RISK_FILTER_OPTIONS}
          onValueChange={handleRiskFilterChange}
        />
      </div>
      {taxBracket > 0 && (
        <div className="rounded bg-primary/10 px-3 py-2 text-sm text-primary">
          Post-tax returns shown — FY2025-26 tax rules
        </div>
      )}
    </div>
  )
}
