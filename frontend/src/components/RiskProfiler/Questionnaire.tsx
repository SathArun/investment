import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useRiskProfilerStore } from '@/store/riskProfilerStore'
import { ScoreMeter } from './ScoreMeter'
import { CompliancePack } from './CompliancePack'

interface FormValues {
  clientId: string
  responses: Record<string, string>
}

export function Questionnaire() {
  const questions = useRiskProfilerStore((s) => s.questions)
  const clients = useRiskProfilerStore((s) => s.clients)
  const profile = useRiskProfilerStore((s) => s.profile)
  const isLoadingQuestions = useRiskProfilerStore((s) => s.isLoadingQuestions)
  const isSubmitting = useRiskProfilerStore((s) => s.isSubmitting)
  const fetchQuestions = useRiskProfilerStore((s) => s.fetchQuestions)
  const fetchClients = useRiskProfilerStore((s) => s.fetchClients)
  const createClient = useRiskProfilerStore((s) => s.createClient)
  const submitProfile = useRiskProfilerStore((s) => s.submitProfile)

  const [showAddClient, setShowAddClient] = useState(false)
  const [newClientName, setNewClientName] = useState('')
  const [newClientAge, setNewClientAge] = useState('')
  const [addingClient, setAddingClient] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: { clientId: '', responses: {} },
  })

  useEffect(() => {
    fetchQuestions()
    fetchClients()
  }, [fetchQuestions, fetchClients])

  const watchedResponses = watch('responses')
  const answeredCount = questions.filter((q) => {
    const val = watchedResponses?.[q.id]
    return val !== undefined && val !== null && val !== ''
  }).length
  const allAnswered = questions.length > 0 && answeredCount === questions.length

  const handleAddClient = async () => {
    if (!newClientName.trim()) return
    setAddingClient(true)
    const client = await createClient(newClientName.trim(), Number(newClientAge) || 0)
    setAddingClient(false)
    if (client) {
      setShowAddClient(false)
      setNewClientName('')
      setNewClientAge('')
      setValue('clientId', client.id)
    }
  }

  const onSubmit = async (values: FormValues) => {
    const responses: Record<string, number> = {}
    for (const [qId, val] of Object.entries(values.responses)) {
      responses[qId] = Number(val)
    }
    await submitProfile(values.clientId, responses, '')
  }

  if (isLoadingQuestions) {
    return (
      <div className="flex justify-center py-12">
        <p className="text-muted-foreground">Loading questions...</p>
      </div>
    )
  }

  return (
    <div>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Client selector */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label htmlFor="clientId" className="block text-sm font-medium text-muted-foreground">
              Select Client
            </label>
            <button
              type="button"
              onClick={() => setShowAddClient((v) => !v)}
              className="text-xs text-blue-600 hover:text-blue-800 font-medium"
            >
              {showAddClient ? 'Cancel' : '+ Add new client'}
            </button>
          </div>
          <select
            id="clientId"
            {...register('clientId', { required: 'Please select a client' })}
            className="w-full border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Select client --</option>
            {clients.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          {errors.clientId && (
            <p className="text-red-500 text-xs mt-1">{errors.clientId.message}</p>
          )}
          {showAddClient && (
            <div className="mt-2 p-3 border border-blue-200 rounded-md bg-blue-50 space-y-2">
              <p className="text-xs font-semibold text-blue-700">New Client</p>
              <input
                type="text"
                placeholder="Full name *"
                value={newClientName}
                onChange={(e) => setNewClientName(e.target.value)}
                className="w-full border border-border rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="number"
                placeholder="Age"
                min={1}
                max={120}
                value={newClientAge}
                onChange={(e) => setNewClientAge(e.target.value)}
                className="w-full border border-border rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="button"
                onClick={handleAddClient}
                disabled={addingClient || !newClientName.trim()}
                className="w-full bg-blue-600 text-white rounded px-3 py-1.5 text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {addingClient ? 'Saving...' : 'Save Client'}
              </button>
            </div>
          )}
        </div>

        {/* Questions */}
        {questions.map((question, idx) => (
          <div key={question.id} className="p-4 bg-card rounded-lg border border-border">
            <p className="text-sm font-medium text-foreground mb-3">
              {idx + 1}. {question.text}
            </p>
            <div className="space-y-2">
              {question.options.map((opt) => (
                <label
                  key={opt.value}
                  className="flex items-start gap-2 cursor-pointer"
                >
                  <input
                    type="radio"
                    value={opt.value}
                    {...register(`responses.${question.id}`, {
                      required: 'Please answer this question',
                    })}
                    className="mt-0.5"
                  />
                  <span className="text-sm text-muted-foreground">{opt.label}</span>
                </label>
              ))}
            </div>
            {errors.responses?.[question.id] && (
              <p className="text-red-500 text-xs mt-1">
                {errors.responses[question.id]?.message}
              </p>
            )}
          </div>
        ))}

        {questions.length > 0 && (
          <button
            type="submit"
            disabled={!allAnswered || isSubmitting}
            className="w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Submitting...' : 'Submit Risk Profile'}
          </button>
        )}
      </form>

      {profile && (
        <div className="mt-8 space-y-6">
          <div className="p-6 bg-card rounded-lg border border-border shadow-sm">
            <h2 className="text-lg font-semibold text-foreground mb-4 text-center">
              Risk Assessment Result
            </h2>
            <ScoreMeter category={profile.risk_category} score={profile.risk_score} />
            {profile.risk_description && (
              <p className="mt-4 text-sm text-muted-foreground text-center">{profile.risk_description}</p>
            )}
          </div>
          <CompliancePack profileId={profile.id} />
        </div>
      )}
    </div>
  )
}
