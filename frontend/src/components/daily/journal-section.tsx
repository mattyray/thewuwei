"use client";

import { useState } from "react";

import type { JournalEntry } from "@/types/api";

interface JournalSectionProps {
  journal: JournalEntry | null;
}

const TRUNCATE_LENGTH = 300;

export function JournalSection({ journal }: JournalSectionProps) {
  const [expanded, setExpanded] = useState(false);

  if (!journal) return null;

  const isLong = journal.content.length > TRUNCATE_LENGTH;
  const displayContent =
    !expanded && isLong
      ? journal.content.slice(0, TRUNCATE_LENGTH) + "..."
      : journal.content;

  return (
    <div>
      <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-text-muted">
        Journal
      </h4>
      <p className="whitespace-pre-wrap text-sm leading-relaxed text-text-primary">
        {displayContent}
      </p>
      {isLong && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-1 text-xs text-accent-primary hover:underline cursor-pointer"
        >
          {expanded ? "Show less" : "Read more"}
        </button>
      )}
      {journal.reflection && (
        <p className="mt-2 whitespace-pre-wrap text-sm italic leading-relaxed text-text-secondary">
          {journal.reflection}
        </p>
      )}
    </div>
  );
}
