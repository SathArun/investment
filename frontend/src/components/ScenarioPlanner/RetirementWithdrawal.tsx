import { useMemo, useState } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { simulateWithdrawal } from '@/utils/retirement'
import { formatCurrency } from '@/utils/riskLabel'

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
    <div className="bg-white border border-gray-200 rounded p-3 shadow text-sm">
      <p className="font-semibold text-gray-700 mb-1">Year {label}</p>
      {payload.map((entry) => (
        <p key={entry.name} style={{ color: entry.color }}>
          Balance: {formatCurrency(entry.value)}
        </p>
      ))}
    </div>
  )
}

const MIN_CORPUS = 1_000_000

export function RetirementWithdrawal() {
  const [corpus, setCorpus] = useState(10_000_000)
  const [monthlyWithdrawal, setMonthlyWithdrawal] = useState(50_000)
  const [returnPct, setReturnPct] = useState(8)
  const [maxYears, setMaxYears] = useState(40)

  const corpusError = corpus < MIN_CORPUS ? 'Minimum corpus \u20b910 lakh' : null

  const result = useMemo(
    () =>
      corpus >= MIN_CORPUS
        ? simulateWithdrawal(corpus, monthlyWithdrawal, returnPct / 100, maxYears)
        : null,
    [corpus, monthlyWithdrawal, returnPct, maxYears],
  )

  const chartData = useMemo(
    () =>
      result
        ? result.yearlyBalances.map((balance, i) => ({ year: i + 1, balance }))
        : [],
    [result],
  )

  const areaColor = useMemo(() => {
    if (!result || result.yearlyBalances.length === 0) return '#22c55e'
    const lastBalance = result.yearlyBalances[result.yearlyBalances.length - 1]
    const ratio = lastBalance / corpus
    if (ratio > 0.5) return '#22c55e'   // green
    if (ratio > 0.2) return '#eab308'   // yellow
    return '#ef4444'                     // red
  }, [result, corpus])

  const yAxisFormatter = (value: number) => {
    if (value >= 10_000_000) return `${(value / 10_000_000).toFixed(1)}Cr`
    if (value >= 100_000) return `${(value / 100_000).toFixed(1)}L`
    return value.toLocaleString('en-IN')
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Retirement Withdrawal Simulator</h2>

      {/* Inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div>
          <label htmlFor="rw-corpus" className="block text-sm font-medium text-gray-700 mb-1">
            Initial Corpus (&#8377;)
          </label>
          <input
            id="rw-corpus"
            type="number"
            min={MIN_CORPUS}
            value={corpus}
            onChange={(e) => setCorpus(Number(e.target.value))}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {corpusError && (
            <p className="text-red-500 text-xs mt-1">{corpusError}</p>
          )}
        </div>

        <div>
          <label htmlFor="rw-withdrawal" className="block text-sm font-medium text-gray-700 mb-1">
            Monthly Withdrawal (&#8377;)
          </label>
          <input
            id="rw-withdrawal"
            type="number"
            min={1000}
            value={monthlyWithdrawal}
            onChange={(e) => setMonthlyWithdrawal(Number(e.target.value))}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="rw-return" className="block text-sm font-medium text-gray-700 mb-1">
            Expected Return %
          </label>
          <input
            id="rw-return"
            type="number"
            min={0}
            max={20}
            step={0.1}
            value={returnPct}
            onChange={(e) => setReturnPct(Number(e.target.value))}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="rw-maxyears" className="block text-sm font-medium text-gray-700 mb-1">
            Max Simulation Years
          </label>
          <input
            id="rw-maxyears"
            type="number"
            min={10}
            max={60}
            value={maxYears}
            onChange={(e) => setMaxYears(Number(e.target.value))}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Summary */}
      {result && (
        <div className="mb-6">
          {result.exhausted ? (
            <p className="text-red-600 font-semibold text-base" data-testid="exhaustion-warning">
              &#9888; Corpus exhausted in {result.yearsLasted} years
            </p>
          ) : (
            <p className="text-green-700 font-semibold text-base" data-testid="corpus-duration">
              Corpus lasts {result.yearsLasted}+ years
            </p>
          )}
        </div>
      )}

      {/* Chart */}
      {chartData.length > 0 && (
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={chartData} margin={{ top: 8, right: 16, left: 16, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="year"
              label={{ value: 'Year', position: 'insideBottomRight', offset: -8 }}
              tick={{ fontSize: 12 }}
            />
            <YAxis tickFormatter={yAxisFormatter} tick={{ fontSize: 12 }} width={60} />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="balance"
              name="Balance"
              stroke={areaColor}
              fill={areaColor}
              fillOpacity={0.2}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
