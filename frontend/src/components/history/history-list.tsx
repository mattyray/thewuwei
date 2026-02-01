"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useJournalEntries } from "@/hooks/use-journal";

import { EntryCard } from "./entry-card";

export function HistoryList() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useJournalEntries(page);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent-primary border-t-transparent" />
      </div>
    );
  }

  if (!data || data.results.length === 0) {
    return (
      <div className="py-12 text-center">
        <p className="text-text-muted">No journal entries yet.</p>
        <p className="mt-1 text-sm text-text-muted">
          Start journaling through the chat on your dashboard.
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-col gap-3">
        {data.results.map((entry) => (
          <EntryCard key={entry.id} entry={entry} />
        ))}
      </div>

      {/* Pagination */}
      <div className="mt-6 flex items-center justify-between">
        <Button
          variant="secondary"
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={!data.previous}
        >
          Previous
        </Button>
        <span className="text-sm text-text-muted">
          Page {page} of {Math.ceil(data.count / 50)}
        </span>
        <Button
          variant="secondary"
          onClick={() => setPage((p) => p + 1)}
          disabled={!data.next}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
