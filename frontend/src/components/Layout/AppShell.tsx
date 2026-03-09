import { cn } from '@/lib/utils'
import { useUIStore } from '@/store/uiStore'

interface AppShellProps {
  sidebar: React.ReactNode
  children: React.ReactNode
}

export function AppShell({ sidebar, children }: AppShellProps) {
  const isSidebarCollapsed = useUIStore((s) => s.isSidebarCollapsed)

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-2 focus:left-2 focus:p-2 focus:bg-white focus:text-blue-700 focus:rounded"
      >
        Skip to main content
      </a>
      <aside
        aria-label="Application sidebar"
        className={cn(
          'bg-gray-900 flex flex-col shrink-0 transition-[width] duration-300 ease-in-out',
          isSidebarCollapsed ? 'w-16' : 'w-60'
        )}
      >
        {sidebar}
      </aside>
      <main id="main-content" className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}
