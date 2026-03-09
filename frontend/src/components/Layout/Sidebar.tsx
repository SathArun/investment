import { useRef } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useUIStore } from '@/store/uiStore'
import { SidebarNav } from './SidebarNav'
import { SidebarFooter } from './SidebarFooter'
import { cn } from '@/lib/utils'

export function Sidebar() {
  const isSidebarCollapsed = useUIStore((s) => s.isSidebarCollapsed)
  const toggleSidebar = useUIStore((s) => s.toggleSidebar)
  const collapseToggleRef = useRef<HTMLButtonElement>(null)

  function handleToggle() {
    toggleSidebar()
    collapseToggleRef.current?.focus()
  }

  return (
    <div className="flex flex-col h-full">
      {/* Logo/title area */}
      <div className={cn('flex items-center px-4 py-4 border-b border-gray-700', isSidebarCollapsed ? 'justify-center' : 'gap-3')}>
        {!isSidebarCollapsed && (
          <span className="text-white font-semibold text-sm leading-tight">India Investment Analyzer</span>
        )}
      </div>

      {/* Nav */}
      <SidebarNav />

      {/* SidebarFooter */}
      <SidebarFooter />

      {/* Collapse toggle */}
      <button
        ref={collapseToggleRef}
        onClick={handleToggle}
        className="flex items-center justify-center p-3 text-gray-400 hover:text-gray-100 border-t border-gray-700"
        aria-label={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {isSidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>
    </div>
  )
}
