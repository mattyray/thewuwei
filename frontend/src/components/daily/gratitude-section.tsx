import type { GratitudeEntry } from "@/types/api";

interface GratitudeSectionProps {
  gratitude: GratitudeEntry | null;
}

export function GratitudeSection({ gratitude }: GratitudeSectionProps) {
  if (!gratitude || gratitude.items.length === 0) {
    return null;
  }

  return (
    <div>
      <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-text-muted">
        Gratitude
      </h4>
      <ul className="space-y-1">
        {gratitude.items.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-text-primary">
            <span className="mt-0.5 text-text-muted">•</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
