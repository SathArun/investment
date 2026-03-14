import { useEffect, useMemo, useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import apiClient from '@/api/client'

interface StressScenario {
  id: string
  name: string
  nifty50_drawdown_pct: number
  recovery_months: number
  description: string
}

function computeDrawdown(
  scenario: StressScenario,
  equityPct: number,
  debtPct: number,
  goldPct: number
): number {
  return (
    (equityPct / 100) * scenario.nifty50_drawdown_pct +
    (debtPct / 100) * scenario.nifty50_drawdown_pct * 0.2 +
    (goldPct / 100) * scenario.nifty50_drawdown_pct * -0.1
  )
}

function getBarColor(drawdown: number): string {
  if (drawdown <= -40) return '#dc2626' // red-600
  if (drawdown <= -20) return '#ea580c' // orange-600
  if (drawdown <= -10) return '#d97706' // amber-600
  return '#65a30d' // lime-600
}

function getSeverityColor(drawdown: number): string {
  if (drawdown <= -40) return 'text-red-700 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-900/20 dark:border-red-900'
  if (drawdown <= -20) return 'text-orange-700 bg-orange-50 border-orange-200 dark:text-orange-400 dark:bg-orange-900/20 dark:border-orange-900'
  if (drawdown <= -10) return 'text-amber-700 bg-amber-50 border-amber-200 dark:text-amber-400 dark:bg-amber-900/20 dark:border-amber-900'
  return 'text-lime-700 bg-lime-50 border-lime-200 dark:text-lime-400 dark:bg-lime-900/20 dark:border-lime-900'
}

function getShortName(name: string): string {
  if (name.includes('COVID')) return 'COVID-19'
  if (name.includes('Financial Crisis')) return 'GFC 2008'
  if (name.includes('Rate Hike')) return 'Rate Hike'
  if (name.includes('Demonet')) return 'Demonet.'
  return name.slice(0, 10)
}

export function StressTest() {
  const [scenarios, setScenarios] = useState<StressScenario[]>([])
  const [loading, setLoading] = useState(true)
  const [equityPct, setEquityPct] = useState(60)
  const [debtPct, setDebtPct] = useState(30)
  const [goldPct, setGoldPct] = useState(10)

  useEffect(() => {
    void apiClient
      .get<StressScenario[]>('/scenarios/stress-test')
      .then((res) => {
        setScenarios(res.data)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  const total = equityPct + debtPct + goldPct
  const allocationValid = total === 100

  const scenarioResults = useMemo(
    () =>
      scenarios.map((s) => ({
        ...s,
        drawdown: computeDrawdown(s, equityPct, debtPct, goldPct),
      })),
    [scenarios, equityPct, debtPct, goldPct]
  )

  const chartData = scenarioResults.map((s) => ({
    name: getShortName(s.name),
    recovery_months: s.recovery_months,
    drawdown: s.drawdown,
  }))

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12" data-testid="loading-spinner">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
        <span className="ml-3 text-muted-foreground">Loading stress test scenarios...</span>
      </div>
    )
  }

  return (
    <div className="bg-card rounded-lg border p-6 space-y-6">
      <h2 className="text-xl font-semibold text-foreground">Portfolio Stress Test</h2>

      {/* Asset Mix Sliders */}
      <div className="bg-muted rounded-lg p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-muted-foreground">Asset Allocation</h3>
          <span
            className={`text-sm font-medium ${allocationValid ? 'text-green-600' : 'text-red-600'}`}
          >
            Total: {total}%
          </span>
        </div>

        {!allocationValid && (
          <p className="text-sm text-red-600 font-medium" role="alert">
            Allocations must total 100%
          </p>
        )}

        <div className="space-y-3">
          <div>
            <label htmlFor="equity-slider" className="flex justify-between text-sm text-muted-foreground mb-1">
              <span>Equity</span>
              <span className="font-medium">{equityPct}%</span>
            </label>
            <input
              id="equity-slider"
              type="range"
              min={0}
              max={100}
              value={equityPct}
              onChange={(e) => setEquityPct(Number(e.target.value))}
              className="w-full accent-blue-600"
              aria-label="Equity percentage"
            />
          </div>

          <div>
            <label htmlFor="debt-slider" className="flex justify-between text-sm text-muted-foreground mb-1">
              <span>Debt</span>
              <span className="font-medium">{debtPct}%</span>
            </label>
            <input
              id="debt-slider"
              type="range"
              min={0}
              max={100}
              value={debtPct}
              onChange={(e) => setDebtPct(Number(e.target.value))}
              className="w-full accent-green-600"
              aria-label="Debt percentage"
            />
          </div>

          <div>
            <label htmlFor="gold-slider" className="flex justify-between text-sm text-muted-foreground mb-1">
              <span>Gold</span>
              <span className="font-medium">{goldPct}%</span>
            </label>
            <input
              id="gold-slider"
              type="range"
              min={0}
              max={100}
              value={goldPct}
              onChange={(e) => setGoldPct(Number(e.target.value))}
              className="w-full accent-yellow-500"
              aria-label="Gold percentage"
            />
          </div>
        </div>
      </div>

      {/* Scenario Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {scenarioResults.map((scenario) => {
          const colorClass = getSeverityColor(scenario.drawdown)
          return (
            <div
              key={scenario.id}
              className={`rounded-lg border p-4 ${colorClass}`}
              data-testid={`scenario-card-${scenario.id}`}
            >
              <h4 className="font-semibold text-sm mb-1">{scenario.name}</h4>
              <p className="text-xs opacity-80 mb-3">{scenario.description}</p>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs opacity-70">Est. Drawdown</p>
                  <p className="text-2xl font-bold" data-testid={`drawdown-${scenario.id}`}>
                    {scenario.drawdown.toFixed(1)}%
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs opacity-70">Recovery</p>
                  <p className="text-lg font-semibold" data-testid={`recovery-${scenario.id}`}>
                    {scenario.recovery_months} months
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recovery Bar Chart */}
      <div>
        <h3 className="text-sm font-semibold text-muted-foreground mb-3">Recovery Period by Scenario</h3>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis
              label={{ value: 'Months', angle: -90, position: 'insideLeft', offset: 10 }}
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              formatter={(value: number) => [`${value} months`, 'Recovery']}
            />
            <Bar dataKey="recovery_months" name="Recovery (months)" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={index} fill={getBarColor(entry.drawdown)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
