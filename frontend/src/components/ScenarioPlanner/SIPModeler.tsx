import { useMemo, useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { corpusProjection } from '@/utils/finance'
import { formatCurrency } from '@/utils/riskLabel'

interface ChartPoint {
  year: number
  base: number
  comparison: number
}

interface TooltipPayloadEntry {
  name: string
  value: number
  color: string
}

interface CustomTooltipProps {
  active?: boolean
  payload?: TooltipPayloadEntry[]
  label?: number
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) return null
  return (
    <div className="bg-card border border-border rounded p-3 shadow text-sm">
      <p className="font-semibold text-foreground mb-1">Year {label}</p>
      {payload.map((entry) => (
        <p key={entry.name} style={{ color: entry.color }}>
          {entry.name}: {formatCurrency(entry.value)}
        </p>
      ))}
    </div>
  )
}

export function SIPModeler() {
  const [monthlySip, setMonthlySip] = useState(10000)
  const [stepupPct, setStepupPct] = useState(10)
  const [duration, setDuration] = useState(20)
  const [baseReturn, setBaseReturn] = useState(12)
  const [compReturn, setCompReturn] = useState(8)

  const chartData = useMemo((): ChartPoint[] => {
    const baseSeries = corpusProjection(0, monthlySip, stepupPct / 100, baseReturn / 100, duration)
    const compSeries = corpusProjection(0, monthlySip, stepupPct / 100, compReturn / 100, duration)
    return baseSeries.map((v, i) => ({ year: i + 1, base: v, comparison: compSeries[i] }))
  }, [monthlySip, stepupPct, baseReturn, compReturn, duration])

  const baseCorpus = chartData[chartData.length - 1]?.base ?? 0
  const compCorpus = chartData[chartData.length - 1]?.comparison ?? 0

  // Total invested: sum of yearly SIP amounts (SIP × 12 per year, with step-up)
  const totalInvested = useMemo(() => {
    let total = 0
    let sip = monthlySip
    for (let yr = 0; yr < duration; yr++) {
      total += sip * 12
      sip = sip * (1 + stepupPct / 100)
    }
    return Math.round(total)
  }, [monthlySip, stepupPct, duration])

  const baseGains = baseCorpus - totalInvested
  const compGains = compCorpus - totalInvested
  const extraGains = baseCorpus - compCorpus

  const yAxisFormatter = (value: number) => {
    if (value >= 10000000) return `${(value / 10000000).toFixed(1)}Cr`
    if (value >= 100000) return `${(value / 100000).toFixed(1)}L`
    return value.toLocaleString('en-IN')
  }

  return (
    <div className="bg-card rounded-lg border p-6">
      <h2 className="text-xl font-semibold text-foreground mb-4">SIP Modeler</h2>

      {/* Inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div>
          <label htmlFor="monthly-sip" className="block text-sm font-medium text-muted-foreground mb-1">
            Monthly SIP (₹)
          </label>
          <input
            id="monthly-sip"
            type="number"
            min={500}
            value={monthlySip}
            onChange={(e) => setMonthlySip(Number(e.target.value))}
            className="w-full border border-border rounded px-3 py-2 text-sm bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="stepup-pct" className="block text-sm font-medium text-muted-foreground mb-1">
            Annual Step-Up %
          </label>
          <input
            id="stepup-pct"
            type="number"
            min={0}
            max={30}
            value={stepupPct}
            onChange={(e) => setStepupPct(Number(e.target.value))}
            className="w-full border border-border rounded px-3 py-2 text-sm bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="duration" className="block text-sm font-medium text-muted-foreground mb-1">
            Duration (Years)
          </label>
          <input
            id="duration"
            type="number"
            min={1}
            max={40}
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            className="w-full border border-border rounded px-3 py-2 text-sm bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="base-return" className="block text-sm font-medium text-muted-foreground mb-1">
            Base Return Rate %
          </label>
          <input
            id="base-return"
            type="number"
            min={0.1}
            max={25}
            step={0.1}
            value={baseReturn}
            onChange={(e) => setBaseReturn(Number(e.target.value))}
            className="w-full border border-border rounded px-3 py-2 text-sm bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="comp-return" className="block text-sm font-medium text-muted-foreground mb-1">
            Comparison Return Rate %
          </label>
          <input
            id="comp-return"
            type="number"
            min={0.1}
            max={25}
            step={0.1}
            value={compReturn}
            onChange={(e) => setCompReturn(Number(e.target.value))}
            className="w-full border border-border rounded px-3 py-2 text-sm bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-muted rounded-lg p-4">
          <p className="text-xs text-muted-foreground mb-1">Total Invested</p>
          <p className="text-lg font-bold text-foreground" data-testid="total-invested">
            {formatCurrency(totalInvested)}
          </p>
        </div>

        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
          <p className="text-xs text-muted-foreground mb-1">Projected at {baseReturn}%</p>
          <p className="text-lg font-bold text-blue-700 dark:text-blue-300" data-testid="base-corpus">
            {formatCurrency(baseCorpus)}
          </p>
          <p className="text-xs text-blue-500 dark:text-blue-400 mt-1">Gains: {formatCurrency(baseGains)}</p>
        </div>

        <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
          <p className="text-xs text-muted-foreground mb-1">Projected at {compReturn}%</p>
          <p className="text-lg font-bold text-orange-700 dark:text-orange-300" data-testid="comp-corpus">
            {formatCurrency(compCorpus)}
          </p>
          <p className="text-xs text-orange-500 dark:text-orange-400 mt-1">Gains: {formatCurrency(compGains)}</p>
        </div>

        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
          <p className="text-xs text-muted-foreground mb-1">Extra gains at {baseReturn}%</p>
          <p className="text-lg font-bold text-green-700 dark:text-green-300" data-testid="extra-gains">
            {formatCurrency(extraGains)}
          </p>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={chartData} margin={{ top: 8, right: 16, left: 16, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis
            dataKey="year"
            label={{ value: 'Year', position: 'insideBottomRight', offset: -8 }}
            tick={{ fontSize: 12 }}
          />
          <YAxis tickFormatter={yAxisFormatter} tick={{ fontSize: 12 }} width={60} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line
            type="monotone"
            dataKey="base"
            name={`${baseReturn}% return`}
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="comparison"
            name={`${compReturn}% return`}
            stroke="#f97316"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
