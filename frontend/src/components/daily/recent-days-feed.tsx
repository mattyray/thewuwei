"use client";

import { useRecentSummaries } from "@/hooks/use-daily-summary";

import { DaySection } from "./day-section";

export function RecentDaysFeed() {
  const { data: summaries, isLoading } = useRecentSummaries(5);

  if (isLoading) {
    return (
      <p className="py-4 text-center text-sm text-text-muted">
        Loading recent days...
      </p>
    );
  }

  if (!summaries || summaries.length === 0) return null;

  return (
    <div className="pt-2">
      {/* Clear divider between today and past days */}
      <div className="mb-4 flex items-center gap-3">
        <div className="h-px flex-1 bg-border" />
        <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
          Previous Days
        </span>
        <div className="h-px flex-1 bg-border" />
      </div>

      <div className="space-y-2">
        {summaries.map((summary) => (
          <DaySection
            key={summary.date}
            summary={summary}
            isToday={false}
            defaultExpanded={false}
          />
        ))}
      </div>
    </div>
  );
}
