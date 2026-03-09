import { LogOut, User } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useDashboardStore } from '@/store/dashboardStore'
import { useUIStore } from '@/store/uiStore'
import { DataFreshnessBar } from '@/components/Dashboard/DataFreshness'

export function SidebarFooter() {
  const advisor = useAuthStore((s) => s.advisor)
  const logout = useAuthStore((s) => s.logout)
  const dataFreshness = useDashboardStore((s) => s.dataFreshness)
  const isSidebarCollapsed = useUIStore((s) => s.isSidebarCollapsed)
  const navigate = useNavigate()

  const advisorName = advisor?.name ?? 'Advisor'

  return (
    <div className="mt-auto border-t border-gray-700 p-3 space-y-2">
      {!isSidebarCollapsed && dataFreshness && (
        <DataFreshnessBar freshness={dataFreshness} />
      )}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <User className="w-4 h-4 text-gray-400 shrink-0" />
          {!isSidebarCollapsed && (
            <div className="min-w-0">
              <p className="text-xs text-gray-300 truncate">{advisorName}</p>
              {advisor?.email && (
                <p className="text-xs text-gray-500 truncate">{advisor.email}</p>
              )}
            </div>
          )}
        </div>
        <button
          onClick={() => { logout(); navigate('/login') }}
          className="text-gray-400 hover:text-gray-100 shrink-0"
          aria-label="Sign out"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
