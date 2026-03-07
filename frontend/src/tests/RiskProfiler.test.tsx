import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { Questionnaire } from '@/components/RiskProfiler/Questionnaire'
import { ScoreMeter } from '@/components/RiskProfiler/ScoreMeter'
import { CompliancePack } from '@/components/RiskProfiler/CompliancePack'

// Mock the store
vi.mock('@/store/riskProfilerStore')
// Mock apiClient for CompliancePack
vi.mock('@/api/client')

import { useRiskProfilerStore } from '@/store/riskProfilerStore'
import apiClient from '@/api/client'

const mockFetchQuestions = vi.fn()
const mockFetchClients = vi.fn()
const mockSubmitProfile = vi.fn()

function makeQuestion(id: string, text: string) {
  return {
    id,
    text,
    category: 'general',
    options: [
      { value: 1, label: 'Low', score: 1 },
      { value: 2, label: 'Medium', score: 2 },
      { value: 3, label: 'High', score: 3 },
    ],
  }
}

const EIGHTEEN_QUESTIONS = Array.from({ length: 18 }, (_, i) =>
  makeQuestion(`q${i + 1}`, `Question ${i + 1}`)
)

const defaultStoreState = {
  questions: [] as ReturnType<typeof makeQuestion>[],
  clients: [{ id: 'client-1', name: 'Alice' }],
  profile: null,
  isLoadingQuestions: false,
  isSubmitting: false,
  fetchQuestions: mockFetchQuestions,
  fetchClients: mockFetchClients,
  submitProfile: mockSubmitProfile,
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(useRiskProfilerStore).mockImplementation(
    (selector: (s: typeof defaultStoreState) => unknown) => selector(defaultStoreState)
  )
})

describe('Questionnaire', () => {
  it('loads questions on mount', () => {
    render(<Questionnaire />)
    expect(mockFetchQuestions).toHaveBeenCalledTimes(1)
    expect(mockFetchClients).toHaveBeenCalledTimes(1)
  })

  it('submit disabled when not all questions answered', () => {
    vi.mocked(useRiskProfilerStore).mockImplementation(
      (selector: (s: typeof defaultStoreState) => unknown) =>
        selector({ ...defaultStoreState, questions: EIGHTEEN_QUESTIONS })
    )

    render(<Questionnaire />)
    const button = screen.getByRole('button', { name: /submit risk profile/i })
    expect(button).toBeDisabled()
  })

  it('shows riskometer after submission', async () => {
    const profileResult = {
      id: 'profile-1',
      risk_score: 42,
      risk_category: 'Moderate',
      risk_description: 'Balanced risk taker',
      retention_until: '2027-01-01',
    }

    let currentState = { ...defaultStoreState, questions: EIGHTEEN_QUESTIONS, profile: null as typeof profileResult | null }

    mockSubmitProfile.mockImplementation(async () => {
      currentState = { ...currentState, profile: profileResult }
      vi.mocked(useRiskProfilerStore).mockImplementation(
        (selector: (s: typeof currentState) => unknown) => selector(currentState)
      )
    })

    vi.mocked(useRiskProfilerStore).mockImplementation(
      (selector: (s: typeof currentState) => unknown) => selector(currentState)
    )

    const { rerender } = render(<Questionnaire />)

    // Select client
    fireEvent.change(screen.getByLabelText(/select client/i), {
      target: { value: 'client-1' },
    })

    // Answer all 18 questions
    EIGHTEEN_QUESTIONS.forEach((q) => {
      const radios = screen.getAllByDisplayValue('1')
      const radio = radios.find((r) => {
        const form = r.closest('form')
        return form !== null
      })
      if (radio) fireEvent.click(radio)
      // Use name-based selection
      const allRadios = screen.getAllByRole('radio')
      const firstForQ = allRadios.find((r) => (r as HTMLInputElement).name === `responses.${q.id}`)
      if (firstForQ) fireEvent.click(firstForQ)
    })

    fireEvent.click(screen.getByRole('button', { name: /submit risk profile/i }))

    await waitFor(() => {
      expect(mockSubmitProfile).toHaveBeenCalled()
    })

    rerender(<Questionnaire />)

    await waitFor(() => {
      expect(screen.getByText('Moderate')).toBeInTheDocument()
    })
  })
})

describe('CompliancePack', () => {
  it('compliance pack button disabled with short rationale', () => {
    render(<CompliancePack profileId="profile-1" />)
    const textarea = screen.getByRole('textbox')
    fireEvent.change(textarea, { target: { value: 'Short text' } })
    const button = screen.getByRole('button', { name: /generate compliance pack/i })
    expect(button).toBeDisabled()
  })

  it('compliance pack button enabled with 50+ char rationale', () => {
    render(<CompliancePack profileId="profile-1" />)
    const textarea = screen.getByRole('textbox')
    const longText = 'A'.repeat(50)
    fireEvent.change(textarea, { target: { value: longText } })
    const button = screen.getByRole('button', { name: /generate compliance pack/i })
    expect(button).not.toBeDisabled()
  })

  it('generates compliance pack and opens PDF', async () => {
    const mockBlob = new Blob(['pdf-content'], { type: 'application/pdf' })
    vi.mocked(apiClient.post).mockResolvedValue({ data: mockBlob })

    const mockOpen = vi.fn()
    vi.stubGlobal('open', mockOpen)

    const mockCreateObjectURL = vi.fn(() => 'blob:http://localhost/fake-url')
    vi.stubGlobal('URL', { createObjectURL: mockCreateObjectURL })

    render(<CompliancePack profileId="profile-1" />)
    const textarea = screen.getByRole('textbox')
    fireEvent.change(textarea, { target: { value: 'A'.repeat(50) } })
    fireEvent.click(screen.getByRole('button', { name: /generate compliance pack/i }))

    await waitFor(() => {
      expect(vi.mocked(apiClient.post)).toHaveBeenCalledWith(
        '/pdf/compliance-pack',
        { risk_profile_id: 'profile-1' },
        { responseType: 'blob' }
      )
    })
  })
})

describe('ScoreMeter', () => {
  it('renders correct category', () => {
    render(<ScoreMeter category="Conservative" score={25} />)
    expect(screen.getByText('Conservative')).toBeInTheDocument()
    expect(screen.getByText('Score: 25')).toBeInTheDocument()
  })

  it('renders Aggressive category', () => {
    render(<ScoreMeter category="Aggressive" score={90} />)
    expect(screen.getByText('Aggressive')).toBeInTheDocument()
    expect(screen.getByText('Score: 90')).toBeInTheDocument()
  })

  it('renders Moderate category', () => {
    render(<ScoreMeter category="Moderate" score={55} />)
    expect(screen.getByText('Moderate')).toBeInTheDocument()
    expect(screen.getByText('Score: 55')).toBeInTheDocument()
  })
})
