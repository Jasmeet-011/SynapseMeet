"use client";

interface Props {
  level: number; // 0 to 1
  active: boolean;
}

export function WaveformVisualizer({ level, active }: Props) {
  const bars = 12;

  return (
    <div className="flex items-center gap-0.5 h-8">
      {Array.from({ length: bars }).map((_, i) => {
        const randomFactor = Math.sin(i * 0.8) * 0.4 + 0.6;
        const height = active ? Math.max(4, level * 32 * randomFactor) : 4;
        return (
          <div
            key={i}
            className={`w-1 rounded-full transition-all duration-100 ${
              active ? "bg-brand-400" : "bg-gray-700"
            }`}
            style={{ height: `${height}px` }}
          />
        );
      })}
    </div>
  );
}
