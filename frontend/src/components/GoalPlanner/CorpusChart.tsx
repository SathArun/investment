import { useState, useMemo } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { formatCurrency } from '@/utils/riskLabel'
import { corpusProjection } from '@/utils/finance'

interface CorpusProjectionData {
  conservative: number[]
  base: number[]
  optimistic: number[]
}

interface CorpusChartProps {
  corpusData: CorpusProjectionData
  currentCorpus: number
  monthlySip: number
  annualStepup: number
}

export function CorpusChart({
  corpusData,
  currentCorpus,
  monthlySip,
  annualStepup: initialStepup,
}: CorpusChartProps) {
  const [previewStepup, setPreviewStepup] = useState<number>(initialStepup)

  const years = corpusData.base.length

  // Client-side preview: recompute base projection with adjusted step-up
  const previewSeries = useMemo(() => {
    // Use 10% as base return for preview
    return corpusProjection(currentCorpus, monthlySip, previewStepup / 100, 0.1, years)
  }, [currentCorpus, monthlySip, previewStepup, years])

  const chartData = useMemo(() => {
    return Array.from({ length: years }, (_, i) => ({
      year: i + 1,
      conservative: corpusData.conservative[i] ?? 0,
      base: corpusData.base[i] ?? 0,
      optimistic: corpusData.optimistic[i] ?? 0,
      preview: previewSeries[i] ?? 0,
    }))
  }, [corpusData, previewSeries, years])

  return (
    <div className="bg-white rounded-lg border p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700">Corpus Projection</h3>
        <div className="flex items-center gap-3 text-sm">
          <label htmlFor="stepup-slider" className="text-gray-600 whitespace-nowrap">
            Step-Up Preview: {previewStepup}%
          </label>
          <input
            id="stepup-slider"
            type="range"
            min={0}
            max={30}
            step={1}
            value={previewStepup}
            onChange={(e) => setPreviewStepup(Number(e.target.value))}
            className="w-32"
          />
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
          <defs>
            <linearGradient id="colorConservative" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#9ca3af" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#9ca3af" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorBase" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorOptimistic" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorPreview" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="year"
            tickFormatter={(v: number) => `Yr ${v}`}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            tickFormatter={(v: number) => formatCurrency(v)}
            tick={{ fontSize: 11 }}
            width={80}
          />
          <Tooltip
            formatter={(value: number, name: string) => [formatCurrency(value), name]}
            labelFormatter={(label: number) => `Year ${label}`}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="conservative"
            name="Conservative"
            stroke="#9ca3af"
            fill="url(#colorConservative)"
            strokeWidth={2}
          />
          <Area
            type="monotone"
            dataKey="base"
            name="Base"
            stroke="#3b82f6"
            fill="url(#colorBase)"
            strokeWidth={2}
          />
          <Area
            type="monotone"
            dataKey="optimistic"
            name="Optimistic"
            stroke="#10b981"
            fill="url(#colorOptimistic)"
            strokeWidth={2}
          />
          <Area
            type="monotone"
            dataKey="preview"
            name="Step-Up Preview"
            stroke="#f59e0b"
            fill="url(#colorPreview)"
            strokeWidth={2}
            strokeDasharray="5 5"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
