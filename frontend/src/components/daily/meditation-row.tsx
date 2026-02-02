import type { DailyCheckin } from "@/types/api";

interface MeditationRowProps {
  checkin: DailyCheckin | null;
}

export function MeditationRow({ checkin }: MeditationRowProps) {
  const completed = checkin?.meditation_completed ?? false;
  const duration = checkin?.meditation_duration;

  return (
    <div className="flex items-center gap-2.5">
      <div
        className={`flex h-5 w-5 items-center justify-center rounded-full border ${
          completed
            ? "border-success bg-success/20 text-success"
            : "border-border text-transparent"
        }`}
      >
        {completed && (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="h-3 w-3"
          >
            <path
              fillRule="evenodd"
              d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
              clipRule="evenodd"
            />
          </svg>
        )}
      </div>
      <span
        className={`text-sm ${
          completed ? "text-text-primary" : "text-text-secondary"
        }`}
      >
        Meditation{duration ? ` · ${duration} min` : ""}
      </span>
    </div>
  );
}
