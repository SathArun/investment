import { useUIStore } from '@/store/uiStore'

export function ViewToggle() {
  const isClientView = useUIStore((s) => s.isClientView)
  const setClientView = useUIStore((s) => s.setClientView)
  const setSidebarCollapsed = useUIStore((s) => s.setSidebarCollapsed)

  function handleAdvisorView() {
    setClientView(false)
  }

  function handleClientView() {
    setClientView(true)
    setSidebarCollapsed(true)
  }

  return (
    <fieldset className="inline-flex rounded-lg bg-gray-100 p-1 gap-0.5">
      <legend className="sr-only">View mode</legend>

      <label className="relative cursor-pointer">
        <input
          type="radio"
          name="view-toggle"
          value="advisor"
          className="sr-only peer"
          checked={!isClientView}
          onChange={handleAdvisorView}
        />
        <span className="block px-4 py-1.5 rounded-md text-sm font-medium transition-all text-gray-600 peer-checked:bg-white peer-checked:text-gray-900 peer-checked:shadow-sm">
          Advisor View
        </span>
      </label>

      <label className="relative cursor-pointer">
        <input
          type="radio"
          name="view-toggle"
          value="client"
          className="sr-only peer"
          checked={isClientView}
          onChange={handleClientView}
        />
        <span className="block px-4 py-1.5 rounded-md text-sm font-medium transition-all text-gray-600 peer-checked:bg-white peer-checked:text-gray-900 peer-checked:shadow-sm">
          Client View
        </span>
      </label>
    </fieldset>
  )
}
