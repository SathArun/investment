# Content Area Dark Modernization — Design Notes
Date: 2026-03-09
Status: Approved

## Problem
The collapsible dark sidebar (spec 003) created a visual mismatch: left side is dark, right side is still hardcoded bg-white throughout. The dark mode CSS token system is already fully wired in index.css but the dark class is never applied to <html>.

## Design Decisions

### 1. Full dark mode via .dark class on <html>
- isDarkMode state in uiStore, defaults to true, persisted to localStorage key 'theme'
- Root useEffect in App.tsx: document.documentElement.classList.toggle('dark', isDarkMode)
- All shadcn/ui components automatically flip (they already consume --background, --card, --muted tokens)

### 2. Color token migration (hardcoded → semantic)
| Old | New |
|-----|-----|
| bg-white | bg-card |
| bg-gray-50 | bg-muted |
| text-gray-900 | text-foreground |
| text-gray-500/600 | text-muted-foreground |
| border-gray-200 | border-border |
| bg-gray-100 | bg-muted |
| hover:bg-gray-50 | hover:bg-muted/50 |
| bg-yellow-50 | bg-yellow-500/10 |
| bg-blue-50 | bg-primary/10 |

### 3. Recharts dark-safe colors
Recharts SVG elements don't consume CSS variables. Override explicitly:
- CartesianGrid stroke: `hsl(var(--border))`
- Axis ticks fill: `hsl(var(--muted-foreground))`
- CustomTooltip: bg-card border-border text-foreground

### 4. Full-width layout + GoalForm two-column
- Remove max-w-* constraints from all App.tsx page containers
- GoalForm: `lg:grid lg:grid-cols-2 lg:gap-8` — form fields left, results cards right
- Padding: py-6 → py-4 for tighter vertical rhythm

### 5. Theme toggle in SidebarFooter
- Button variant="ghost" size="icon" with Moon (dark) / Sun (light) lucide icon
- When collapsed: icon only; when expanded: icon + label
- Calls toggleTheme() from uiStore

### 6. FilterBar → shadcn Select
- Replace raw @radix-ui/react-select with shadcn Select (already installed as src/components/ui/select.tsx)
- Automatically inherits dark mode tokens

## Parking Lot (future specs)
- GoalForm native inputs → shadcn Input
- ScenariosPage horizontal layout
