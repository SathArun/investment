import { useState, useEffect } from 'react'
import apiClient from '@/api/client'
import { useDashboardStore } from '@/store/dashboardStore'
import { useFilterStore } from '@/store/filterStore'
import { useUIStore } from '@/store/uiStore'
import { ShareWhatsApp } from './ShareWhatsApp'
import { ProductPinCard } from './ProductPinCard'

interface Client {
  id: string
  name: string
}

export function ProductPins() {
  const products = useDashboardStore((s) => s.products)
  const pinnedProducts = useDashboardStore((s) => s.pinnedProducts)
  const togglePin = useDashboardStore((s) => s.togglePin)
  const taxBracket = useFilterStore((s) => s.taxBracket)
  const timeHorizon = useFilterStore((s) => s.timeHorizon)
  const isClientView = useUIStore((s) => s.isClientView)
  const [isGenerating, setIsGenerating] = useState(false)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [clients, setClients] = useState<Client[]>([])
  const [selectedClientId, setSelectedClientId] = useState('')

  useEffect(() => {
    apiClient.get('/clients').then(({ data }) => {
      const list: Client[] = data.clients ?? data
      setClients(list)
      if (list.length > 0) setSelectedClientId(list[0].id)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    return () => {
      if (pdfUrl) URL.revokeObjectURL(pdfUrl)
    }
  }, [pdfUrl])

  const pinnedList = products.filter((p) => pinnedProducts.has(p.id))
  const pinCount = pinnedProducts.size
  const tooMany = pinCount > 5

  const handleGeneratePdf = async () => {
    if (pinCount === 0 || tooMany || !selectedClientId) return
    setIsGenerating(true)
    setMessage(null)
    try {
      const response = await apiClient.post(
        '/pdf/client-report',
        {
          client_id: selectedClientId,
          product_ids: [...pinnedProducts].map(String),
          tax_bracket: taxBracket,
          time_horizon: timeHorizon,
        },
        { responseType: 'blob' },
      )
      const blob = new Blob([response.data as BlobPart], { type: 'application/pdf' })
      const url = URL.createObjectURL(blob)
      setPdfUrl(url)
      window.open(url, '_blank', 'noopener,noreferrer')
      setMessage('PDF generated successfully!')
    } catch {
      setMessage('PDF generation failed')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="bg-card rounded-lg border p-4">
      {isClientView ? (
        // Client view: hero card grid
        <div>
          {pinnedList.length === 0 ? (
            <p className="text-muted-foreground text-sm py-4 text-center">
              Pin products in Advisor View to build your comparison
            </p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
              {pinnedList.map((p) => (
                <ProductPinCard key={p.id} product={p} onUnpin={togglePin} />
              ))}
            </div>
          )}
          {/* PDF + WhatsApp buttons always visible in client view */}
          <div className="space-y-3 mt-4">
            {clients.length > 0 ? (
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Client</label>
                <select
                  value={selectedClientId}
                  onChange={(e) => setSelectedClientId(e.target.value)}
                  className="w-full border border-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {clients.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
            ) : (
              <p className="text-xs text-amber-600">No clients found — add a client in Goal Planner or Risk Profiler first.</p>
            )}
            <div className="flex items-center gap-3">
              <button
                onClick={handleGeneratePdf}
                disabled={pinCount === 0 || tooMany || isGenerating || !selectedClientId}
                className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isGenerating ? 'Generating...' : 'Generate PDF Report'}
              </button>
              {pdfUrl && <ShareWhatsApp pdfUrl={pdfUrl} />}
            </div>
          </div>
          {message && (
            <p role="status" className={`mt-2 text-sm ${message.includes('failed') ? 'text-red-500' : 'text-green-600'}`}>
              {message}
            </p>
          )}
        </div>
      ) : (
        // Advisor view: keep EXISTING list layout exactly as-is
        <div>
          <h3 className="font-semibold text-foreground mb-3">Selected Products ({pinCount}/5)</h3>
          {pinnedList.length === 0 ? (
            <p className="text-muted-foreground text-sm">Pin products from the table below to compare them</p>
          ) : (
            <ul className="space-y-1 mb-4">
              {pinnedList.map((p) => (
                <li key={p.id} className="text-sm text-muted-foreground">{p.name}</li>
              ))}
            </ul>
          )}
          {tooMany && <p className="text-red-500 text-sm mb-3">Select 1–5 products</p>}
          <div className="space-y-3">
            {clients.length > 0 ? (
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Client</label>
                <select
                  value={selectedClientId}
                  onChange={(e) => setSelectedClientId(e.target.value)}
                  className="w-full border border-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {clients.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
            ) : (
              <p className="text-xs text-amber-600">No clients found — add a client in Goal Planner or Risk Profiler first.</p>
            )}
            <div className="flex items-center gap-3">
              <button
                onClick={handleGeneratePdf}
                disabled={pinCount === 0 || tooMany || isGenerating || !selectedClientId}
                className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isGenerating ? 'Generating...' : 'Generate PDF Report'}
              </button>
              {pdfUrl && <ShareWhatsApp pdfUrl={pdfUrl} />}
            </div>
          </div>
          {message && (
            <p role="status" className={`mt-2 text-sm ${message.includes('failed') ? 'text-red-500' : 'text-green-600'}`}>
              {message}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
