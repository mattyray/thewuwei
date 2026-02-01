"use client";

import { useState } from "react";

import type { JournalEntry } from "@/types/api";

export function EntryCard({ entry }: { entry: JournalEntry }) {
  const [expanded, setExpanded] = useState(false);

  const date = new Date(entry.date + "T00:00:00");
  const formatted = date.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <button
      onClick={() => setExpanded(!expanded)}
      className="w-full rounded-xl border border-border bg-bg-secondary p-4 text-left transition-colors hover:border-bg-tertiary cursor-pointer"
    >
      <div className="flex items-baseline justify-between gap-4">
        <p className="text-sm font-medium text-text-primary line-clamp-2">
          {entry.content}
        </p>
        <span className="shrink-0 text-xs text-text-muted">{formatted}</span>
      </div>

      {expanded && (
        <div className="mt-3 space-y-3 border-t border-border pt-3">
          <div>
            <p className="mb-1 text-xs font-medium uppercase text-text-muted">
              Entry
            </p>
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-text-secondary">
              {entry.content}
            </p>
          </div>

          {entry.reflection && (
            <div>
              <p className="mb-1 text-xs font-medium uppercase text-text-muted">
                Reflection
              </p>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-text-secondary italic">
                {entry.reflection}
              </p>
            </div>
          )}
        </div>
      )}
    </button>
  );
}
