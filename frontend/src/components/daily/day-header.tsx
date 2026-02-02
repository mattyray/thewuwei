"use client";

import type { DailySummary } from "@/types/api";

interface DayHeaderProps {
  date: string;
  isToday: boolean;
  isExpanded: boolean;
  onToggle: () => void;
  summary?: DailySummary;
}

function formatDate(dateStr: string, isToday: boolean): string {
  if (isToday) return "Today";
  const d = new Date(dateStr + "T12:00:00");
  const now = new Date();
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);

  if (dateStr === yesterday.toISOString().split("T")[0]) return "Yesterday";

  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

function formatFullDate(dateStr: string): string {
  const d = new Date(dateStr + "T12:00:00");
  return d.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

function buildSummaryLine(summary?: DailySummary): string {
  if (!summary) return "";
  const parts: string[] = [];

  if (summary.checkin?.meditation_completed) {
    const dur = summary.checkin.meditation_duration;
    parts.push(dur ? `Meditated ${dur}min` : "Meditated");
  }
  if (summary.gratitude) {
    const count = summary.gratitude.items.length;
    parts.push(`${count} gratitude${count !== 1 ? "s" : ""}`);
  }
  if (summary.journal) {
    parts.push("Journaled");
  }
  if (summary.todos.length > 0) {
    parts.push(`${summary.todos.length} todo${summary.todos.length !== 1 ? "s" : ""}`);
  }

  return parts.join(" · ");
}

export function DayHeader({
  date,
  isToday,
  isExpanded,
  onToggle,
  summary,
}: DayHeaderProps) {
  const label = formatDate(date, isToday);
  const fullDate = formatFullDate(date);
  const summaryLine = buildSummaryLine(summary);

  return (
    <button
      onClick={onToggle}
      className="flex w-full items-center gap-3 py-2 text-left"
    >
      {!isToday && (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className={`h-4 w-4 shrink-0 text-text-muted transition-transform ${
            isExpanded ? "rotate-90" : ""
          }`}
        >
          <path
            fillRule="evenodd"
            d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
            clipRule="evenodd"
          />
        </svg>
      )}
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-2">
          <span className="text-sm font-semibold uppercase tracking-wider text-text-muted">
            {label}
          </span>
          <span className="text-xs text-text-muted">{fullDate}</span>
        </div>
        {!isExpanded && summaryLine && (
          <p className="mt-0.5 truncate text-xs text-text-muted">
            {summaryLine}
          </p>
        )}
      </div>
    </button>
  );
}
