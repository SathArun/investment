import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { LoginForm } from '@/components/Login/LoginForm'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { AppShell } from '@/components/Layout/AppShell'
import { Sidebar } from '@/components/Layout/Sidebar'
import { FilterBar } from '@/components/Dashboard/FilterBar'
import { AssetTable } from '@/components/Dashboard/AssetTable'
import { ScoreBreakdown } from '@/components/Dashboard/ScoreBreakdown'
import { RiskReturnPlot } from '@/components/Dashboard/RiskReturnPlot'
import { ViewToggle } from '@/components/Presentation/ViewToggle'
import { FilterSummary } from '@/components/Dashboard/FilterSummary'
import { ProductPins } from '@/components/Presentation/ProductPins'
import { Questionnaire } from '@/components/RiskProfiler/Questionnaire'
import { GoalForm } from '@/components/GoalPlanner/GoalForm'
import { SIPModeler } from '@/components/ScenarioPlanner/SIPModeler'
import { StressTest } from '@/components/ScenarioPlanner/StressTest'
import { RetirementWithdrawal } from '@/components/ScenarioPlanner/RetirementWithdrawal'
import { useDashboardStore } from '@/store/dashboardStore'
import { useUIStore } from '@/store/uiStore'
import { useAdminStore } from '@/store/adminStore'
import { JobCard } from '@/components/Admin/JobCard'
import { Skeleton } from '@/components/ui/skeleton'

function DashboardPage() {
  const isClientView = useUIStore((s) => s.isClientView)
  const setSelectedProduct = useUIStore((s) => s.setSelectedProduct)
  const fetchProducts = useDashboardStore((s) => s.fetchProducts)

  useEffect(() => {
    fetchProducts(0, 'long', 'All')
  }, [fetchProducts])

  return (
    <>
      <div className="px-6 py-3 flex items-center justify-between border-b bg-white">
        {isClientView ? <FilterSummary /> : <FilterBar />}
        <ViewToggle />
      </div>
      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        <ProductPins />
        <AssetTable isClientView={isClientView} onSelectProduct={setSelectedProduct} />
        {!isClientView && <RiskReturnPlot />}
        {!isClientView && <ScoreBreakdown />}
      </main>
    </>
  )
}

function GoalsPage() {
  return (
    <main className="max-w-4xl mx-auto px-6 py-6">
      <GoalForm />
    </main>
  )
}

function RiskProfilerPage() {
  return (
    <main className="max-w-4xl mx-auto px-6 py-6">
      <Questionnaire />
    </main>
  )
}

function ScenariosPage() {
  return (
    <main className="max-w-5xl mx-auto px-6 py-6 space-y-8">
      <SIPModeler />
      <StressTest />
      <RetirementWithdrawal />
    </main>
  )
}

function AdminPage() {
  const { jobs, isLoading, error, fetchJobs, triggerJob } = useAdminStore()

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  useEffect(() => {
    const id = setInterval(() => {
      const { jobs: currentJobs } = useAdminStore.getState()
      const hasRunning = currentJobs.some((j) => j.latest_status === 'running')
      // Always fetch; interval is fixed at 5s when running, 30s otherwise.
      // Because we cannot dynamically change an interval without recreating it,
      // we check inside the callback and skip the slower-cadence ticks.
      if (hasRunning) {
        fetchJobs()
      }
    }, 5_000)
    return () => clearInterval(id)
  }, [fetchJobs])

  useEffect(() => {
    const id = setInterval(() => {
      const { jobs: currentJobs } = useAdminStore.getState()
      const hasRunning = currentJobs.some((j) => j.latest_status === 'running')
      if (!hasRunning) {
        fetchJobs()
      }
    }, 30_000)
    return () => clearInterval(id)
  }, [fetchJobs])

  return (
    <main className="max-w-7xl mx-auto px-6 py-6">
      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded text-sm">{error}</div>
      )}
      {isLoading && jobs.length === 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-[140px] rounded-lg motion-reduce:animate-none" />
          ))}
        </div>
      ) : !error && jobs.length === 0 ? (
        <div className="text-gray-400 text-sm">No jobs found. Ensure the backend is running and try refreshing.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <JobCard key={job.job_name} job={job} onRunNow={triggerJob} />
          ))}
        </div>
      )}
    </main>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route
          element={
            <ProtectedRoute>
              <AppShell sidebar={<Sidebar />}>
                <Outlet />
              </AppShell>
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/goals" element={<GoalsPage />} />
          <Route path="/risk-profiler" element={<RiskProfilerPage />} />
          <Route path="/scenarios" element={<ScenariosPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
