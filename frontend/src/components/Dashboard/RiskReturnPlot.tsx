import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
  Cell,
} from 'recharts'
import { useDashboardStore } from '@/store/dashboardStore'
import { useUIStore } from '@/store/uiStore'

const CATEGORY_COLORS: Record<string, string> = {
  eq_largecap: '#3b82f6',
  eq_midcap: '#60a5fa',
  eq_smallcap: '#1d4ed8',
  eq_flexicap: '#2563eb',
  eq_index: '#93c5fd',
  eq_elss: '#1e40af',
  debt_liquid: '#10b981',
  debt_shortterm: '#34d399',
  debt_corporate: '#059669',
  debt_gilt: '#6ee7b7',
  hybrid: '#8b5cf6',
  gold: '#f59e0b',
  real_estate: '#ef4444',
  commodity: '#f97316',
  nps: '#ec4899',
}
const DEFAULT_COLOR = '#94a3b8'

interface ChartPoint {
  x: number
  y: number
  r: number
  name: string
  assetClass: string
}

interface CustomTooltipProps {
  active?: boolean
  payload?: Array<{ payload: ChartPoint }>
  isClientView?: boolean
}

function CustomTooltip({ active, payload, isClientView }: CustomTooltipProps) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload
  return (
    <div className="bg-white border border-gray-200 rounded p-3 shadow text-sm">
      <p className="font-semibold">{point.name}</p>
      <p>{isClientView ? 'Risk Level' : 'Risk (Std Dev)'}: {point.x.toFixed(2)}%</p>
      <p>{isClientView ? 'Annual Return' : 'Post-Tax 3Y'}: {point.y.toFixed(2)}%</p>
      {!isClientView && <p>Advisor Score: {Math.round(point.r * 5)}</p>}
    </div>
  )
}

export function RiskReturnPlot() {
  const products = useDashboardStore((s) => s.products)
  const isClientView = useUIStore((s) => s.isClientView)

  const xLabel = isClientView ? 'Risk Level' : 'Risk (Std Dev)'
  const yLabel = isClientView ? 'Annual Return' : 'Post-Tax Return (3Y)'

  // Filter out products with null std_dev or null post_tax_return_3y
  const validProducts = products.filter(
    (p) => p.std_dev_3y !== null && p.post_tax_return_3y !== null
  )

  // Group by asset_class
  const groupedByClass = validProducts.reduce<Record<string, ChartPoint[]>>((acc, p) => {
    const point: ChartPoint = {
      x: (p.std_dev_3y as number) * 100,
      y: (p.post_tax_return_3y as number) * 100,
      r: p.advisor_score / 5,
      name: p.name,
      assetClass: p.asset_class,
    }
    if (!acc[p.asset_class]) {
      acc[p.asset_class] = []
    }
    acc[p.asset_class].push(point)
    return acc
  }, {})

  const assetClasses = Object.keys(groupedByClass)

  return (
    <div className="bg-white rounded-lg border p-4">
      <h3 className="font-semibold text-gray-700 mb-3">Risk vs Return</h3>
      <ResponsiveContainer width="100%" height={350}>
        <ScatterChart margin={{ top: 10, right: 30, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="x"
            type="number"
            name={xLabel}
            label={{ value: xLabel, position: 'insideBottom', offset: -10 }}
            domain={['auto', 'auto']}
          />
          <YAxis
            dataKey="y"
            type="number"
            name={yLabel}
            label={{ value: yLabel, angle: -90, position: 'insideLeft' }}
            domain={['auto', 'auto']}
          />
          <RechartsTooltip content={<CustomTooltip isClientView={isClientView} />} />
          {!isClientView && <Legend verticalAlign="top" />}
          {assetClasses.map((assetClass) => (
            <Scatter
              key={assetClass}
              name={assetClass}
              data={groupedByClass[assetClass]}
              fill={CATEGORY_COLORS[assetClass] ?? DEFAULT_COLOR}
            >
              {groupedByClass[assetClass].map((point, index) => (
                <Cell
                  key={`${assetClass}-${index}`}
                  fill={CATEGORY_COLORS[point.assetClass] ?? DEFAULT_COLOR}
                  r={point.r}
                />
              ))}
            </Scatter>
          ))}
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}
