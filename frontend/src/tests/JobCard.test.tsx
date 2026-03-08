import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { JobCard } from '@/components/Admin/JobCard'
import type { AdminJobSummary } from '@/store/adminStore'

function makeJob(overrides: Partial<AdminJobSummary> = {}): AdminJobSummary {
  return {
    job_name: 'ingest_amfi',
    latest_status: 'success',
    latest_started_at: new Date().toISOString(),
    latest_duration_seconds: 12.5,
    runs: [],
    ...overrides,
  }
}

describe('JobCard', () => {
  it('renders job name', () => {
    render(<JobCard job={makeJob({ job_name: 'ingest_amfi' })} onRunNow={vi.fn()} />)
    expect(screen.getByText('ingest_amfi')).toBeInTheDocument()
  })

  it('shows green "success" badge when latest_status is success', () => {
    render(<JobCard job={makeJob({ latest_status: 'success' })} onRunNow={vi.fn()} />)
    const badge = screen.getByText('success')
    expect(badge).toBeInTheDocument()
    // Verify green styling class
    expect(badge.className).toMatch(/green/)
  })

  it('shows red "failed" badge when latest_status is failed', () => {
    render(<JobCard job={makeJob({ latest_status: 'failed' })} onRunNow={vi.fn()} />)
    const badge = screen.getByText('failed')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toMatch(/red/)
  })

  it('shows spinning "running" badge when latest_status is running', () => {
    render(<JobCard job={makeJob({ latest_status: 'running' })} onRunNow={vi.fn()} />)
    expect(screen.getByText('running')).toBeInTheDocument()
    // The spinning icon character is rendered alongside
    expect(screen.getByText('⟳')).toBeInTheDocument()
  })

  it('shows "Never run" when latest_status is never_run', () => {
    render(
      <JobCard
        job={makeJob({ latest_status: 'never_run', latest_started_at: null })}
        onRunNow={vi.fn()}
      />
    )
    expect(screen.getByText('Never run')).toBeInTheDocument()
  })

  it('Run Now button is DISABLED when latest_status is running', () => {
    render(<JobCard job={makeJob({ latest_status: 'running' })} onRunNow={vi.fn()} />)
    // When running the button text changes to 'Running...'
    const btn = screen.getByRole('button', { name: /running\.\.\./i })
    expect(btn).toBeDisabled()
  })

  it('Run Now button is ENABLED when latest_status is success', () => {
    render(<JobCard job={makeJob({ latest_status: 'success' })} onRunNow={vi.fn()} />)
    const btn = screen.getByRole('button', { name: /run now/i })
    expect(btn).not.toBeDisabled()
  })

  it('calls onRunNow with job_name when Run Now button is clicked', () => {
    const onRunNow = vi.fn()
    render(<JobCard job={makeJob({ job_name: 'ingest_amfi' })} onRunNow={onRunNow} />)
    fireEvent.click(screen.getByRole('button', { name: /run now/i }))
    expect(onRunNow).toHaveBeenCalledWith('ingest_amfi')
  })
})
