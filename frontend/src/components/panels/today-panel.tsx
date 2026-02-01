"use client";

import { Card } from "@/components/ui/card";
import { useCheckin } from "@/hooks/use-checkin";
import { useTodayGratitude } from "@/hooks/use-gratitude";

function CheckRow({
  label,
  checked,
}: {
  label: string;
  checked: boolean;
}) {
  return (
    <div className="flex items-center gap-2.5 py-1">
      <div
        className={`flex h-5 w-5 items-center justify-center rounded-full border ${
          checked
            ? "border-success bg-success/20 text-success"
            : "border-border text-transparent"
        }`}
      >
        {checked && (
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
          checked ? "text-text-primary" : "text-text-secondary"
        }`}
      >
        {label}
      </span>
    </div>
  );
}

export function TodayPanel() {
  const { data: checkin, isLoading } = useCheckin();
  const { data: gratitude } = useTodayGratitude();

  if (isLoading) {
    return (
      <Card title="Today">
        <p className="text-sm text-text-muted">Loading...</p>
      </Card>
    );
  }

  return (
    <Card title="Today">
      <CheckRow
        label="Meditate"
        checked={checkin?.meditation_completed ?? false}
      />
      <CheckRow
        label="Gratitude"
        checked={checkin?.gratitude_completed ?? (gratitude != null)}
      />
      <CheckRow
        label="Journal"
        checked={checkin?.journal_completed ?? false}
      />
    </Card>
  );
}
