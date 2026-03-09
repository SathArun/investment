import { useMemo } from 'react'
import * as Tooltip from '@radix-ui/react-tooltip'
import { useFilterStore } from '@/store/filterStore'
import { useDashboardStore } from '@/store/dashboardStore'
import { getRiskColor, getRiskLabel, formatPct, formatCurrency } from '@/utils/riskLabel'
import type { ProductRow } from '@/types/product'
import { Skeleton } from '@/components/ui/skeleton'

interface AssetTableProps {
  isClientView?: boolean
  onSelectProduct?: (product: ProductRow | null) => void
}

type SortKey = keyof Pick<
  ProductRow,
  'name' | 'sebi_risk_level' | 'cagr_1y' | 'cagr_3y' | 'cagr_5y' | 'post_tax_return_3y' | 'advisor_score'
>

const SORTABLE_COLUMNS: { key: SortKey; label: string; highlight?: boolean }[] = [
  { key: 'name', label: 'Product Name' },
  { key: 'sebi_risk_level', label: 'SEBI Risk' },
  { key: 'cagr_1y', label: '1Y CAGR' },
  { key: 'cagr_3y', label: '3Y CAGR' },
  { key: 'cagr_5y', label: '5Y CAGR' },
  { key: 'post_tax_return_3y', label: 'Post-Tax 3Y', highlight: true },
  { key: 'advisor_score', label: 'Advisor Score' },
]

export const CLIENT_VIEW_COLUMNS = [
  'name', 'sebi_risk_level', 'cagr_1y', 'cagr_3y', 'cagr_5y', 'post_tax_return_3y',
] as const

function getSortValue(product: ProductRow, key: SortKey): number | string {
  const val = product[key]
  if (val === null || val === undefined) return -Infinity
  return val
}

export function AssetTable({ isClientView = false, onSelectProduct }: AssetTableProps) {
  const { sortBy, sortDir, setSortBy, setSortDir } = useFilterStore()
  const { products, isLoading, pinnedProducts, togglePin } = useDashboardStore()

  const visibleColumns = isClientView
    ? SORTABLE_COLUMNS.filter((col) => (CLIENT_VIEW_COLUMNS as readonly string[]).includes(col.key))
    : SORTABLE_COLUMNS

  const sortedProducts = useMemo(() => {
    const sorted = [...products].sort((a, b) => {
      const aVal = getSortValue(a, sortBy as SortKey)
      const bVal = getSortValue(b, sortBy as SortKey)

      let cmp = 0
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        cmp = aVal - bVal
      } else {
        cmp = String(aVal).localeCompare(String(bVal))
      }

      return sortDir === 'asc' ? cmp : -cmp
    })

    // Pinned products first
    return [
      ...sorted.filter((p) => pinnedProducts.has(p.id)),
      ...sorted.filter((p) => !pinnedProducts.has(p.id)),
    ]
  }, [products, sortBy, sortDir, pinnedProducts])

  function handleHeaderClick(key: SortKey) {
    if (sortBy === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(key)
      setSortDir('desc')
    }
  }

  function getSortIndicator(key: SortKey) {
    if (sortBy !== key) return null
    return sortDir === 'asc' ? ' ▲' : ' ▼'
  }

  return (
    <Tooltip.Provider delayDuration={200}>
      <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th className="px-3 py-3 text-center font-medium">Pin</th>
              {visibleColumns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => handleHeaderClick(col.key)}
                  className={`cursor-pointer select-none px-4 py-3 text-left font-medium hover:bg-gray-100 ${
                    col.highlight ? 'bg-blue-50 text-blue-700' : ''
                  } ${sortBy === col.key ? 'text-blue-600' : ''}`}
                >
                  {col.label}
                  {getSortIndicator(col.key)}
                </th>
              ))}
              {!isClientView && (
                <th className="px-4 py-3 text-left font-medium">Breakdown</th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {isLoading && products.length === 0 ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={`skeleton-${i}`}>
                  <td className="px-3 py-3"><Skeleton className="h-7 w-6 motion-reduce:animate-none" /></td>
                  {visibleColumns.map((col) => (
                    <td key={col.key} className="px-4 py-3">
                      <Skeleton className="h-5 w-full motion-reduce:animate-none" />
                    </td>
                  ))}
                  {!isClientView && (
                    <td className="px-4 py-3"><Skeleton className="h-7 w-16 motion-reduce:animate-none" /></td>
                  )}
                </tr>
              ))
            ) : sortedProducts.length === 0 ? (
              <tr>
                <td
                  colSpan={visibleColumns.length + (isClientView ? 1 : 2)}
                  className="px-4 py-8 text-center text-gray-400"
                >
                  No products available
                </td>
              </tr>
            ) : (
              sortedProducts.map((product) => (
                <Tooltip.Root key={product.id}>
                  <Tooltip.Trigger asChild>
                    <tr
                      className={`transition-colors hover:bg-gray-50 ${
                        pinnedProducts.has(product.id) ? 'bg-yellow-50' : ''
                      }`}
                    >
                      <td className="px-3 py-3 text-center">
                        <button
                          onClick={() => togglePin(product.id)}
                          aria-label={`pin-${product.id}`}
                          className={`text-lg leading-none transition-colors ${
                            pinnedProducts.has(product.id)
                              ? 'text-yellow-500'
                              : 'text-gray-300 hover:text-yellow-400'
                          }`}
                        >
                          {pinnedProducts.has(product.id) ? '★' : '☆'}
                        </button>
                      </td>
                      {visibleColumns.map((col) => {
                        switch (col.key) {
                          case 'name':
                            return (
                              <td key="name" className="px-4 py-3 font-medium text-gray-900">
                                {product.name}
                              </td>
                            )
                          case 'sebi_risk_level':
                            return (
                              <td key="sebi_risk_level" className="px-4 py-3">
                                <div className="flex items-center gap-2">
                                  <span
                                    className={`inline-block h-3 w-3 rounded-full ${getRiskColor(
                                      product.sebi_risk_level
                                    )}`}
                                    aria-hidden="true"
                                  />
                                  <span className="text-gray-700">
                                    {getRiskLabel(product.sebi_risk_level)}
                                  </span>
                                </div>
                              </td>
                            )
                          case 'cagr_1y':
                            return (
                              <td key="cagr_1y" className="px-4 py-3 text-gray-700">
                                {formatPct(product.cagr_1y)}
                              </td>
                            )
                          case 'cagr_3y':
                            return (
                              <td key="cagr_3y" className="px-4 py-3 text-gray-700">
                                {formatPct(product.cagr_3y)}
                              </td>
                            )
                          case 'cagr_5y':
                            return (
                              <td key="cagr_5y" className="px-4 py-3 text-gray-700">
                                {formatPct(product.cagr_5y)}
                              </td>
                            )
                          case 'post_tax_return_3y':
                            return (
                              <td key="post_tax_return_3y" className="bg-blue-50 px-4 py-3 font-semibold text-blue-800">
                                {formatPct(product.post_tax_return_3y)}
                              </td>
                            )
                          case 'advisor_score':
                            return (
                              <td key="advisor_score" className="px-4 py-3 text-gray-700">
                                {Math.round(product.advisor_score)}
                              </td>
                            )
                          default:
                            return null
                        }
                      })}
                      {!isClientView && (
                        <td className="px-4 py-3">
                          <button
                            onClick={() => onSelectProduct?.(product)}
                            className="rounded bg-blue-600 px-2 py-1 text-xs font-medium text-white hover:bg-blue-700"
                            aria-label={`score-breakdown-${product.id}`}
                          >
                            Details
                          </button>
                        </td>
                      )}
                    </tr>
                  </Tooltip.Trigger>
                  <Tooltip.Portal>
                    <Tooltip.Content
                      side="top"
                      className="z-50 rounded-lg border border-gray-200 bg-white px-4 py-3 shadow-xl text-sm"
                      sideOffset={4}
                    >
                      <div className="grid grid-cols-2 gap-x-6 gap-y-1">
                        <span className="text-gray-500">10Y CAGR</span>
                        <span className="font-medium text-gray-800">
                          {formatPct(product.cagr_10y)}
                        </span>
                        <span className="text-gray-500">Std Dev</span>
                        <span className="font-medium text-gray-800">
                          {formatPct(product.std_dev_3y)}
                        </span>
                        <span className="text-gray-500">Max Drawdown</span>
                        <span className="font-medium text-gray-800">
                          {formatPct(product.max_drawdown_5y)}
                        </span>
                        <span className="text-gray-500">Expense Ratio</span>
                        <span className="font-medium text-gray-800">
                          {formatPct(product.expense_ratio)}
                        </span>
                        <span className="text-gray-500">Min Investment</span>
                        <span className="font-medium text-gray-800">
                          {formatCurrency(product.min_investment_inr)}
                        </span>
                        <span className="text-gray-500">Liquidity</span>
                        <span className="font-medium text-gray-800">
                          {product.liquidity_label ?? '—'}
                        </span>
                      </div>
                      <Tooltip.Arrow className="fill-white" />
                    </Tooltip.Content>
                  </Tooltip.Portal>
                </Tooltip.Root>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Tooltip.Provider>
  )
}
