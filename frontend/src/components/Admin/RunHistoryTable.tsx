import { RunRow } from '@/store/adminStore'

interface RunHistoryTableProps {
  runs: RunRow[]
}

function StatusBadge({ status }: { status: RunRow['status'] }) {
  if (status === 'success') {
    return (
      <span className="px-1.5 py-0.5 rounded text-xs bg-green-100 text-green-700">success</span>
    )
  }
  if (status === 'failed') {
    return (
      <span className="px-1.5 py-0.5 rounded text-xs bg-red-100 text-red-700">failed</span>
    )
  }
  if (status === 'running') {
    return (
      <span className="px-1.5 py-0.5 rounded text-xs bg-blue-100 text-blue-700">running</span>
    )
  }
  return null
}

export function RunHistoryTable({ runs }: RunHistoryTableProps) {
  return (
    <table className="w-full text-xs">
      <thead>
        <tr className="text-left text-gray-500 border-b">
          <th className="pb-1 pr-2 font-medium">Time</th>
          <th className="pb-1 pr-2 font-medium">Status</th>
          <th className="pb-1 pr-2 font-medium">Duration</th>
          <th className="pb-1 pr-2 font-medium">Rows</th>
          <th className="pb-1 font-medium">Error</th>
        </tr>
      </thead>
      <tbody>
        {runs.map((run) => {
          const errorText = run.error_msg ?? '—'
          const truncatedError =
            errorText.length > 50 ? errorText.slice(0, 50) + '…' : errorText
          return (
            <tr key={run.id} className="border-b last:border-0">
              <td className="py-1 pr-2 text-gray-600">
                {new Date(run.started_at).toLocaleString('en-IN')}
              </td>
              <td className="py-1 pr-2">
                <StatusBadge status={run.status} />
              </td>
              <td className="py-1 pr-2 text-gray-600">
                {run.duration_seconds != null ? run.duration_seconds.toFixed(1) + 's' : '—'}
              </td>
              <td className="py-1 pr-2 text-gray-600">{run.rows_affected ?? '—'}</td>
              <td className="py-1 text-gray-600">{truncatedError}</td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}
