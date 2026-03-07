import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate, NavLink } from 'react-router-dom'
import { LoginForm } from '@/components/Login/LoginForm'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { FilterBar } from '@/components/Dashboard/FilterBar'
import { AssetTable } from '@/components/Dashboard/AssetTable'
import { ScoreBreakdown } from '@/components/Dashboard/ScoreBreakdown'
import { RiskReturnPlot } from '@/components/Dashboard/RiskReturnPlot'
import { ClientViewToggle } from '@/components/Presentation/ClientViewToggle'
import { ProductPins } from '@/components/Presentation/ProductPins'
import { Questionnaire } from '@/components/RiskProfiler/Questionnaire'
import { GoalForm } from '@/components/GoalPlanner/GoalForm'
import { SIPModeler } from '@/components/ScenarioPlanner/SIPModeler'
import { StressTest } from '@/components/ScenarioPlanner/StressTest'
import { RetirementWithdrawal } from '@/components/ScenarioPlanner/RetirementWithdrawal'
import { useAuthStore } from '@/store/authStore'
import { useDashboardStore } from '@/store/dashboardStore'
import { useUIStore } from '@/store/uiStore'

const NAV_LINKS = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/goals', label: 'Goal Planner' },
  { to: '/risk-profiler', label: 'Risk Profiler' },
  { to: '/scenarios', label: 'Scenarios' },
]

function AppNav({ title }: { title: string }) {
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  return (
    <nav className="bg-white border-b px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-6">
        <span className="text-xl font-bold text-gray-900">{title}</span>
        <div className="flex items-center gap-1">
          {NAV_LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </div>
      </div>
      <button
        onClick={() => {
          logout()
          navigate('/login')
        }}
        className="text-sm text-gray-500 hover:text-gray-700"
      >
        Sign out
      </button>
    </nav>
  )
}

function DashboardPage() {
  const isClientView = useUIStore((s) => s.isClientView)
  const setSelectedProduct = useUIStore((s) => s.setSelectedProduct)
  const fetchProducts = useDashboardStore((s) => s.fetchProducts)

  useEffect(() => {
    fetchProducts(0, 'long', 'All')
  }, [fetchProducts])

  return (
    <div className="min-h-screen bg-gray-50">
      <AppNav title="India Investment Analyzer" />
      <div className="bg-white border-b px-6 py-2 flex justify-end">
        <ClientViewToggle />
      </div>
      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        <FilterBar />
        {isClientView && <ProductPins />}
        <AssetTable isClientView={isClientView} onSelectProduct={setSelectedProduct} />
        <RiskReturnPlot />
        <ScoreBreakdown />
      </main>
    </div>
  )
}

function GoalsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <AppNav title="Goal Planner" />
      <main className="max-w-4xl mx-auto px-6 py-6">
        <GoalForm />
      </main>
    </div>
  )
}

function RiskProfilerPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <AppNav title="Risk Profiler" />
      <main className="max-w-4xl mx-auto px-6 py-6">
        <Questionnaire />
      </main>
    </div>
  )
}

function ScenariosPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <AppNav title="Scenario Planner" />
      <main className="max-w-5xl mx-auto px-6 py-6 space-y-8">
        <SIPModeler />
        <StressTest />
        <RetirementWithdrawal />
      </main>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/goals" element={<ProtectedRoute><GoalsPage /></ProtectedRoute>} />
        <Route path="/risk-profiler" element={<ProtectedRoute><RiskProfilerPage /></ProtectedRoute>} />
        <Route path="/scenarios" element={<ProtectedRoute><ScenariosPage /></ProtectedRoute>} />
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
