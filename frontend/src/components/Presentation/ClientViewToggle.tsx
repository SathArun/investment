import { useUIStore } from '@/store/uiStore'

export function ClientViewToggle() {
  const isClientView = useUIStore((s) => s.isClientView)
  const toggleClientView = useUIStore((s) => s.toggleClientView)

  return (
    <button
      onClick={toggleClientView}
      className={`px-4 py-2 rounded-md font-medium transition-colors ${
        isClientView
          ? 'bg-blue-600 text-white'
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
      }`}
      aria-pressed={isClientView}
    >
      {isClientView ? 'Client View ON' : 'Client View'}
    </button>
  )
}
