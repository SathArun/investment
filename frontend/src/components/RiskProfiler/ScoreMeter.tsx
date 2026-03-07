const CATEGORY_ANGLES: Record<string, number> = {
  'Conservative': -72,
  'Moderately Conservative': -36,
  'Moderate': 0,
  'Moderately Aggressive': 36,
  'Aggressive': 72,
}

// Convert polar degrees (0=right, CCW) to SVG arc endpoint
// We map our "gauge" space: -90deg=left, +90deg=right (top of semicircle at 0)
// In SVG coords, the arc starts at left (-90deg from positive-x-axis = 180deg SVG)
// Each segment is 36 degrees of the 180-deg semicircle

function polarToXY(angleDeg: number, r: number): { x: number; y: number } {
  // angleDeg: -90 = leftmost, +90 = rightmost
  // SVG: x increases right, y increases down; we draw in upper half (y <= 0)
  const rad = ((angleDeg - 90) * Math.PI) / 180
  return { x: r * Math.cos(rad), y: r * Math.sin(rad) }
}

function arcPath(startAngle: number, endAngle: number, r: number): string {
  const start = polarToXY(startAngle, r)
  const end = polarToXY(endAngle, r)
  // large-arc-flag = 0 since each segment is 36 deg < 180
  return `M 0 0 L ${start.x} ${start.y} A ${r} ${r} 0 0 1 ${end.x} ${end.y} Z`
}

const SEGMENTS = [
  { startAngle: -90, endAngle: -54, color: '#22c55e', label: 'Conservative' },
  { startAngle: -54, endAngle: -18, color: '#86efac', label: 'Moderately Conservative' },
  { startAngle: -18, endAngle: 18,  color: '#facc15', label: 'Moderate' },
  { startAngle: 18,  endAngle: 54,  color: '#f97316', label: 'Moderately Aggressive' },
  { startAngle: 54,  endAngle: 90,  color: '#ef4444', label: 'Aggressive' },
]

export function ScoreMeter({ category, score }: { category: string; score: number }) {
  const angle = CATEGORY_ANGLES[category] ?? 0
  return (
    <div className="flex flex-col items-center">
      <svg width="200" height="110" viewBox="-100 0 200 110">
        {SEGMENTS.map((seg) => (
          <path
            key={seg.label}
            d={arcPath(seg.startAngle, seg.endAngle, 90)}
            fill={seg.color}
            stroke="white"
            strokeWidth="1"
          />
        ))}
        <line
          x1="0" y1="0" x2="0" y2="-85"
          stroke="#1f2937"
          strokeWidth="3"
          strokeLinecap="round"
          transform={`rotate(${angle})`}
        />
        <circle cx="0" cy="0" r="5" fill="#1f2937" />
      </svg>
      <p className="font-semibold text-gray-800">{category}</p>
      <p className="text-gray-500 text-sm">Score: {score}</p>
    </div>
  )
}
