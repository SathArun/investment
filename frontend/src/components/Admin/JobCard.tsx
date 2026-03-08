import { AdminJobSummary } from '@/store/adminStore'
import { RunHistoryTable } from './RunHistoryTable'

interface JobCardProps {
  job: AdminJobSummary
  onRunNow: (jobName: string) => void
}

function StatusBadge({ status }: { status: AdminJobSummary['latest_status'] }) {
  if (status === 'success') {
    return (
      <span className="px-2 py-0.5 rounded text-xs bg-green-100 text-green-700">success</span>
    )
  }
  if (status === 'failed') {
    return (
      <span className="px-2 py-0.5 rounded text-xs bg-red-100 text-red-700">failed</span>
    )
  }
  if (status === 'running') {
    return (
      <span className="px-2 py-0.5 rounded text-xs bg-blue-100 text-blue-700 inline-flex items-center gap-1">
        <span className="inline-block animate-spin">⟳</span>
        running
      </span>
    )
  }
  // never_run
  return (
    <span className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-500">Never run</span>
  )
}

export function JobCard({ job, onRunNow }: JobCardProps) {
  const isRunning = job.latest_status === 'running'

  return (
    <div className="bg-white rounded-lg border p-4 space-y-3">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <span className="font-bold text-gray-900 text-sm">{job.job_name}</span>
        <StatusBadge status={job.latest_status} />
      </div>

      {/* Latest run info */}
      {job.latest_status !== 'never_run' && job.latest_started_at && (
        <div className="text-xs text-gray-500 space-y-0.5">
          <div>Last run: {new Date(job.latest_started_at).toLocaleString()}</div>
          {job.latest_duration_seconds != null && (
            <div>Duration: {job.latest_duration_seconds.toFixed(1)}s</div>
          )}
        </div>
      )}

      {/* Run Now button */}
      <button
        onClick={() => onRunNow(job.job_name)}
        disabled={isRunning}
        className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isRunning ? 'Running...' : 'Run Now'}
      </button>

      {/* Collapsible run history */}
      <details>
        <summary className="text-xs text-gray-500 cursor-pointer select-none">
          Last {job.runs.length} runs
        </summary>
        <div className="mt-2">
          <RunHistoryTable runs={job.runs} />
        </div>
      </details>
    </div>
  )
}
