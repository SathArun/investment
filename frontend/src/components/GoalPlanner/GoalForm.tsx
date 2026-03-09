import { useEffect, useState } from 'react'
import { Skeleton } from '@/components/ui/skeleton'
import { useForm } from 'react-hook-form'
import { useGoalStore } from '@/store/goalStore'
import type { GoalFormData } from '@/store/goalStore'
import { CorpusChart } from '@/components/GoalPlanner/CorpusChart'
import { AllocationPie } from '@/components/GoalPlanner/AllocationPie'
import { formatCurrency, formatPct } from '@/utils/riskLabel'

export function GoalForm() {
  const { clients, currentPlan, isLoadingClients, isLoadingPlan, fetchClients, createClient, createGoalAndFetchPlan } =
    useGoalStore()
  const [showAddClient, setShowAddClient] = useState(false)
  const [newClientName, setNewClientName] = useState('')
  const [newClientAge, setNewClientAge] = useState('')
  const [newClientTax, setNewClientTax] = useState('0')
  const [addingClient, setAddingClient] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<GoalFormData>({
    defaultValues: {
      current_corpus_inr: 0,
      annual_stepup_pct: 10,
      inflation_rate: 6,
    },
  })

  useEffect(() => {
    fetchClients()
  }, [fetchClients])

  const onSubmit = (data: GoalFormData) => {
    createGoalAndFetchPlan({
      ...data,
      target_amount_inr: Number(data.target_amount_inr),
      current_corpus_inr: Number(data.current_corpus_inr),
      monthly_sip_inr: Number(data.monthly_sip_inr),
      annual_stepup_pct: Number(data.annual_stepup_pct),
      inflation_rate: Number(data.inflation_rate),
    })
  }

  const handleAddClient = async () => {
    if (!newClientName.trim()) return
    setAddingClient(true)
    const client = await createClient(newClientName.trim(), Number(newClientAge) || 0, Number(newClientTax))
    setAddingClient(false)
    if (client) {
      setShowAddClient(false)
      setNewClientName('')
      setNewClientAge('')
      setNewClientTax('0')
      setValue('client_id', client.id)
    }
  }

  const watchedValues = watch()

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-lg border p-6 space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Create Goal</h2>

        {/* Client */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label htmlFor="client_id" className="block text-sm font-medium text-gray-700">
              Client
            </label>
            <button
              type="button"
              onClick={() => setShowAddClient((v) => !v)}
              className="text-xs text-blue-600 hover:text-blue-800 font-medium"
            >
              {showAddClient ? 'Cancel' : '+ Add new client'}
            </button>
          </div>
          {isLoadingClients ? (
            <p className="text-sm text-gray-500">Loading clients...</p>
          ) : (
            <select
              id="client_id"
              {...register('client_id', { required: 'Client is required' })}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a client</option>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} (Age: {c.age})
                </option>
              ))}
            </select>
          )}
          {errors.client_id && (
            <p className="text-xs text-red-600 mt-1">{errors.client_id.message}</p>
          )}
          {showAddClient && (
            <div className="mt-2 p-3 border border-blue-200 rounded-md bg-blue-50 space-y-2">
              <p className="text-xs font-semibold text-blue-700">New Client</p>
              <input
                type="text"
                placeholder="Full name *"
                value={newClientName}
                onChange={(e) => setNewClientName(e.target.value)}
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex gap-2">
                <input
                  type="number"
                  placeholder="Age"
                  min={1}
                  max={120}
                  value={newClientAge}
                  onChange={(e) => setNewClientAge(e.target.value)}
                  className="w-1/2 border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <select
                  value={newClientTax}
                  onChange={(e) => setNewClientTax(e.target.value)}
                  className="w-1/2 border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="0">0% Tax</option>
                  <option value="0.05">5% Tax</option>
                  <option value="0.1">10% Tax</option>
                  <option value="0.2">20% Tax</option>
                  <option value="0.3">30% Tax</option>
                </select>
              </div>
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

        {/* Goal Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Goal Name
          </label>
          <input
            id="name"
            type="text"
            placeholder="e.g. Retirement, Child Education"
            {...register('name', { required: 'Goal name is required' })}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.name && (
            <p className="text-xs text-red-600 mt-1">{errors.name.message}</p>
          )}
        </div>

        {/* Target Amount */}
        <div>
          <label htmlFor="target_amount_inr" className="block text-sm font-medium text-gray-700 mb-1">
            Target Amount (₹)
          </label>
          <input
            id="target_amount_inr"
            type="number"
            min={0}
            placeholder="e.g. 10000000"
            {...register('target_amount_inr', {
              required: 'Target amount is required',
              min: { value: 1, message: 'Must be greater than 0' },
            })}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.target_amount_inr && (
            <p className="text-xs text-red-600 mt-1">{errors.target_amount_inr.message}</p>
          )}
        </div>

        {/* Target Date */}
        <div>
          <label htmlFor="target_date" className="block text-sm font-medium text-gray-700 mb-1">
            Target Date
          </label>
          <input
            id="target_date"
            type="date"
            {...register('target_date', { required: 'Target date is required' })}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.target_date && (
            <p className="text-xs text-red-600 mt-1">{errors.target_date.message}</p>
          )}
        </div>

        {/* Current Corpus */}
        <div>
          <label htmlFor="current_corpus_inr" className="block text-sm font-medium text-gray-700 mb-1">
            Current Corpus (₹)
          </label>
          <input
            id="current_corpus_inr"
            type="number"
            min={0}
            {...register('current_corpus_inr', { required: 'Current corpus is required', min: 0 })}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.current_corpus_inr && (
            <p className="text-xs text-red-600 mt-1">{errors.current_corpus_inr.message}</p>
          )}
        </div>

        {/* Monthly SIP */}
        <div>
          <label htmlFor="monthly_sip_inr" className="block text-sm font-medium text-gray-700 mb-1">
            Monthly SIP (₹)
          </label>
          <input
            id="monthly_sip_inr"
            type="number"
            min={0}
            placeholder="e.g. 25000"
            {...register('monthly_sip_inr', {
              required: 'Monthly SIP is required',
              min: { value: 1, message: 'Must be greater than 0' },
            })}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.monthly_sip_inr && (
            <p className="text-xs text-red-600 mt-1">{errors.monthly_sip_inr.message}</p>
          )}
        </div>

        {/* Annual Step-Up % */}
        <div>
          <label htmlFor="annual_stepup_pct" className="block text-sm font-medium text-gray-700 mb-1">
            Annual Step-Up %
          </label>
          <input
            id="annual_stepup_pct"
            type="number"
            min={0}
            max={30}
            step={0.5}
            {...register('annual_stepup_pct', {
              required: 'Annual step-up is required',
              min: 0,
              max: 30,
            })}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.annual_stepup_pct && (
            <p className="text-xs text-red-600 mt-1">{errors.annual_stepup_pct.message}</p>
          )}
        </div>

        {/* Inflation Rate % */}
        <div>
          <label htmlFor="inflation_rate" className="block text-sm font-medium text-gray-700 mb-1">
            Inflation Rate %
          </label>
          <input
            id="inflation_rate"
            type="number"
            min={0}
            max={20}
            step={0.5}
            {...register('inflation_rate', {
              required: 'Inflation rate is required',
              min: 0,
              max: 20,
            })}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.inflation_rate && (
            <p className="text-xs text-red-600 mt-1">{errors.inflation_rate.message}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={isLoadingPlan}
          className="w-full bg-blue-600 text-white rounded px-4 py-2 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoadingPlan ? 'Calculating...' : 'Calculate Plan'}
        </button>
      </form>

      {isLoadingPlan && (
        <div className="space-y-4">
          {/* Summary cards skeleton */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-[88px] rounded-lg motion-reduce:animate-none" />
            ))}
          </div>
          {/* Corpus chart skeleton */}
          <Skeleton className="h-[200px] w-full rounded-lg motion-reduce:animate-none" />
          {/* Allocation pie skeleton */}
          <Skeleton className="h-[200px] w-full rounded-lg motion-reduce:animate-none" />
        </div>
      )}

      {/* Plan results */}
      {currentPlan && !isLoadingPlan && (
        <div className="space-y-6">
          {/* Summary cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg border p-4">
              <p className="text-xs text-gray-500 uppercase tracking-wide">Inflation-Adj. Target</p>
              <p className="text-xl font-bold text-gray-900 mt-1">
                {formatCurrency(currentPlan.inflation_adjusted_target)}
              </p>
            </div>
            <div className="bg-white rounded-lg border p-4">
              <p className="text-xs text-gray-500 uppercase tracking-wide">Required SIP</p>
              <p className="text-xl font-bold text-gray-900 mt-1">
                {formatCurrency(currentPlan.required_sip)}/mo
              </p>
            </div>
            <div className="bg-white rounded-lg border p-4">
              <p className="text-xs text-gray-500 uppercase tracking-wide">Goal Probability</p>
              <p className="text-xl font-bold text-gray-900 mt-1">
                {formatPct(currentPlan.goal_probability)}
              </p>
            </div>
          </div>

          {/* NPS Banner */}
          {currentPlan.nps_highlight && (
            <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-blue-800">
              💡 NPS Tier 1 recommended — qualifies for additional ₹50,000 deduction under 80CCD(1B)
            </div>
          )}

          {/* Corpus Chart */}
          <CorpusChart
            corpusData={currentPlan.corpus_projection}
            currentCorpus={Number(watchedValues.current_corpus_inr) || 0}
            monthlySip={Number(watchedValues.monthly_sip_inr) || 0}
            annualStepup={Number(watchedValues.annual_stepup_pct) || 0}
          />

          {/* Allocation Pie */}
          <AllocationPie allocation={currentPlan.recommended_allocation} />
        </div>
      )}
    </div>
  )
}
