import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'
import { formatPct, getRiskLabel, getRiskColor } from '@/utils/riskLabel'
import type { ProductRow } from '@/types/product'

interface ProductPinCardProps {
  product: ProductRow
  onUnpin: (id: number) => void
}

export function ProductPinCard({ product, onUnpin }: ProductPinCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow duration-200 relative">
      <CardContent className="p-4 space-y-3">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <h3 className="text-lg font-semibold line-clamp-2 leading-tight pr-6">{product.name}</h3>
            </TooltipTrigger>
            <TooltipContent>{product.name}</TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <div className="flex flex-wrap gap-2">
          <Badge variant="secondary" className="text-xs">{product.asset_class}</Badge>
          <span className={cn('px-2 py-0.5 rounded text-xs font-medium text-white', getRiskColor(product.sebi_risk_level))}>
            {getRiskLabel(product.sebi_risk_level)}
          </span>
        </div>

        <div className="space-y-1">
          <p className="text-2xl font-bold text-blue-600">
            {formatPct(product.post_tax_return_3y)}
            <span className="text-sm font-normal text-gray-500 ml-1">post-tax 3Y</span>
          </p>
          {product.cagr_5y !== null && (
            <p className="text-sm text-gray-500">{formatPct(product.cagr_5y)} 5Y CAGR</p>
          )}
        </div>

        <button
          onClick={() => onUnpin(product.id)}
          className="absolute top-3 right-3 text-yellow-500 hover:text-gray-400 transition-colors"
          aria-label={`unpin-${product.id}`}
        >
          ★
        </button>
      </CardContent>
    </Card>
  )
}
