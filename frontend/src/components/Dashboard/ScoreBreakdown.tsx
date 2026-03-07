import * as Dialog from '@radix-ui/react-dialog'
import { useUIStore } from '@/store/uiStore'
import type { ScoreBreakdown as ScoreBreakdownType } from '@/types/product'

interface SubScoreInfo {
  title: string
  description: string
  weight: number
}

const SCORE_DESCRIPTIONS: Record<keyof ScoreBreakdownType, SubScoreInfo> = {
  risk_adjusted: {
    title: 'Risk-Adjusted Return',
    description: 'How well the product compensates for its volatility (Sharpe ratio percentile)',
    weight: 30,
  },
  tax_yield: {
    title: 'Tax Efficiency',
    description: 'Post-tax return relative to peers at your selected tax bracket',
    weight: 25,
  },
  liquidity: {
    title: 'Liquidity',
    description: 'How quickly you can access your money without penalty',
    weight: 15,
  },
  expense: {
    title: 'Low Expense',
    description: 'Minimal fees — lower expense ratio reduces long-term drag on returns',
    weight: 10,
  },
  consistency: {
    title: 'Return Consistency',
    description: 'Stable returns year over year — lower volatility in rolling returns',
    weight: 10,
  },
  goal_fit: {
    title: 'Goal Fit',
    description: "Alignment between this product's risk profile and your selected time horizon",
    weight: 10,
  },
}

const SUB_SCORE_KEYS: (keyof ScoreBreakdownType)[] = [
  'risk_adjusted',
  'tax_yield',
  'liquidity',
  'expense',
  'consistency',
  'goal_fit',
]

function getScoreColor(score: number): string {
  if (score >= 75) return 'bg-emerald-500'
  if (score >= 50) return 'bg-yellow-500'
  return 'bg-red-500'
}

export function ScoreBreakdown() {
  const selectedProduct = useUIStore((s) => s.selectedProduct)
  const setSelectedProduct = useUIStore((s) => s.setSelectedProduct)

  return (
    <Dialog.Root
      open={selectedProduct !== null}
      onOpenChange={(open) => {
        if (!open) setSelectedProduct(null)
      }}
    >
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/40 z-40" />
        <Dialog.Content
          className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl z-50 flex flex-col overflow-y-auto"
          aria-describedby="score-breakdown-description"
        >
          {selectedProduct && (
            <>
              {/* Header */}
              <div className="flex items-start justify-between p-6 border-b border-gray-200">
                <div className="flex-1 pr-4">
                  <Dialog.Title className="text-lg font-semibold text-gray-900 leading-tight">
                    {selectedProduct.name}
                  </Dialog.Title>
                  <p
                    id="score-breakdown-description"
                    className="text-sm text-gray-500 mt-1"
                  >
                    Score breakdown — {selectedProduct.asset_class}
                  </p>
                </div>
                <Dialog.Close
                  className="flex-shrink-0 rounded-md p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                  aria-label="Close panel"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </Dialog.Close>
              </div>

              {/* Composite Score */}
              <div className="px-6 py-5 bg-gray-50 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Advisor Score</span>
                  <span className="text-3xl font-bold text-gray-900">
                    {selectedProduct.advisor_score.toFixed(1)}
                  </span>
                </div>
                <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${getScoreColor(selectedProduct.advisor_score)}`}
                    style={{ width: `${selectedProduct.advisor_score}%` }}
                  />
                </div>
              </div>

              {/* Sub-scores */}
              <div className="flex-1 px-6 py-4 space-y-5">
                <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-400">
                  Sub-Score Breakdown
                </h3>
                {SUB_SCORE_KEYS.map((key) => {
                  const info = SCORE_DESCRIPTIONS[key]
                  const score = selectedProduct.score_breakdown[key]
                  return (
                    <div key={key}>
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex-1">
                          <span className="text-sm font-medium text-gray-800">{info.title}</span>
                          <span className="ml-2 text-xs text-gray-400">({info.weight}%)</span>
                        </div>
                        <span className="text-sm font-semibold text-gray-700 ml-2">
                          {score.toFixed(0)}
                        </span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${getScoreColor(score)}`}
                          style={{ width: `${score}%` }}
                          role="progressbar"
                          aria-valuenow={score}
                          aria-valuemin={0}
                          aria-valuemax={100}
                          aria-label={info.title}
                        />
                      </div>
                      <p className="mt-1 text-xs text-gray-400">{info.description}</p>
                    </div>
                  )
                })}
              </div>
            </>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
