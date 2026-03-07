import { useState } from 'react'
import apiClient from '@/api/client'

export function CompliancePack({ profileId }: { profileId: string }) {
  const [rationale, setRationale] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const canGenerate = rationale.trim().length >= 50

  const handleGenerate = async () => {
    setIsGenerating(true)
    try {
      const response = await apiClient.post(
        '/pdf/compliance-pack',
        { risk_profile_id: profileId },
        { responseType: 'blob' }
      )
      const blob = new Blob([response.data as BlobPart], { type: 'application/pdf' })
      const url = URL.createObjectURL(blob)
      window.open(url, '_blank')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="mt-6 p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Compliance Pack</h3>
      <div className="mb-4">
        <label htmlFor="rationale" className="block text-sm font-medium text-gray-700 mb-1">
          Advisor Rationale
        </label>
        <textarea
          id="rationale"
          value={rationale}
          onChange={(e) => setRationale(e.target.value)}
          rows={4}
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Provide your rationale for this risk profile recommendation..."
        />
        <p className="text-xs text-gray-500 mt-1">
          {rationale.trim().length} / 50 minimum characters
        </p>
      </div>
      <button
        onClick={handleGenerate}
        disabled={!canGenerate || isGenerating}
        className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isGenerating ? 'Generating...' : 'Generate Compliance Pack'}
      </button>
    </div>
  )
}
