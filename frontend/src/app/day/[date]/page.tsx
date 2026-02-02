"use client";

import Link from "next/link";
import { use } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { DaySection } from "@/components/daily/day-section";
import { Header } from "@/components/layout/header";
import { useDailySummary } from "@/hooks/use-daily-summary";

interface Props {
  params: Promise<{ date: string }>;
}

export default function DayPage({ params }: Props) {
  const { date } = use(params);

  return (
    <AuthGuard>
      <Header />
      <DayPageContent date={date} />
    </AuthGuard>
  );
}

function DayPageContent({ date }: { date: string }) {
  const { data: summary, isLoading, error } = useDailySummary(date);

  return (
    <div className="min-h-[calc(100vh-3.5rem)]">
      <div className="mx-auto max-w-3xl px-4 py-6">
        <Link
          href="/"
          className="mb-4 inline-flex items-center gap-1 text-sm text-text-secondary hover:text-text-primary transition-colors"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="h-4 w-4"
          >
            <path
              fillRule="evenodd"
              d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z"
              clipRule="evenodd"
            />
          </svg>
          Back to today
        </Link>

        {isLoading && (
          <p className="py-12 text-center text-sm text-text-muted">
            Loading...
          </p>
        )}

        {error && (
          <p className="py-12 text-center text-sm text-error">
            Failed to load data for this date.
          </p>
        )}

        {summary && (
          <DaySection
            summary={summary}
            isToday={false}
            defaultExpanded={true}
          />
        )}
      </div>
    </div>
  );
}
