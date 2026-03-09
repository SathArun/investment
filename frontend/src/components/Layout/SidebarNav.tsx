import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Target, Activity, BarChart2, Settings } from 'lucide-react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/store/uiStore'

const MAIN_NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/goals', label: 'Goal Planner', icon: Target },
  { to: '/risk-profiler', label: 'Risk Profiler', icon: Activity },
  { to: '/scenarios', label: 'Scenarios', icon: BarChart2 },
]

const ADMIN_NAV = [
  { to: '/admin', label: 'System Health', icon: Settings },
]

function NavItem({ to, label, icon: Icon, dim = false }: {
  to: string
  label: string
  icon: React.ComponentType<{ className?: string }>
  dim?: boolean
}) {
  const isSidebarCollapsed = useUIStore((s) => s.isSidebarCollapsed)

  const item = (
    <NavLink
      to={to}
      aria-label={label}
      className={({ isActive }) =>
        cn(
          'relative flex items-center gap-3 px-3 py-2 rounded mx-2 my-0.5 text-sm font-medium transition-colors',
          isActive
            ? 'bg-gray-800 text-white before:absolute before:left-0 before:top-0 before:bottom-0 before:w-0.5 before:bg-blue-500 before:rounded-l'
            : dim
            ? 'text-gray-500 hover:text-gray-300 hover:bg-gray-800'
            : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
        )
      }
    >
      <Icon className="w-5 h-5 shrink-0" aria-hidden="true" />
      {!isSidebarCollapsed && <span>{label}</span>}
    </NavLink>
  )

  if (isSidebarCollapsed) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>{item}</TooltipTrigger>
          <TooltipContent side="right">{label}</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    )
  }

  return item
}

export function SidebarNav() {
  const isClientView = useUIStore((s) => s.isClientView)

  return (
    <nav className="flex-1 py-2">
      {isClientView ? (
        <NavItem to="/dashboard" label="Dashboard" icon={LayoutDashboard} />
      ) : (
        <>
          {MAIN_NAV.map((link) => (
            <NavItem key={link.to} {...link} />
          ))}
          <div className="mx-2 my-2">
            <Separator className="bg-gray-700" />
          </div>
          {ADMIN_NAV.map((link) => (
            <NavItem key={link.to} {...link} dim />
          ))}
        </>
      )}
    </nav>
  )
}
