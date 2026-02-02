"use client";

import { useState } from "react";

import type { DailySummary } from "@/types/api";

import { ChatTranscript } from "./chat-transcript";
import { DayHeader } from "./day-header";
import { GratitudeSection } from "./gratitude-section";
import { JournalSection } from "./journal-section";
import { MeditationRow } from "./meditation-row";
import { TodosSection } from "./todos-section";

interface DaySectionProps {
  summary: DailySummary;
  isToday?: boolean;
  defaultExpanded?: boolean;
}

export function DaySection({
  summary,
  isToday = false,
  defaultExpanded = false,
}: DaySectionProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  const hasGratitude = summary.gratitude && summary.gratitude.items.length > 0;
  const hasJournal = !!summary.journal;
  const hasTodos = summary.todos.length > 0 || isToday;

  return (
    <div>
      <DayHeader
        date={summary.date}
        isToday={isToday}
        isExpanded={isToday || expanded}
        onToggle={() => {
          if (!isToday) setExpanded(!expanded);
        }}
        summary={summary}
      />

      {(isToday || expanded) && (
        <div className="mt-3 space-y-3">
          {/* Meditation card */}
          <div className="rounded-xl bg-bg-secondary p-4">
            <MeditationRow checkin={summary.checkin} />
          </div>

          {/* Gratitude card */}
          {hasGratitude && (
            <div className="rounded-xl bg-bg-secondary p-4">
              <GratitudeSection gratitude={summary.gratitude} />
            </div>
          )}

          {/* Journal card */}
          {hasJournal && (
            <div className="rounded-xl bg-bg-secondary p-4">
              <JournalSection journal={summary.journal} />
            </div>
          )}

          {/* Todos card */}
          {hasTodos && (
            <div className="rounded-xl bg-bg-secondary p-4">
              <TodosSection todos={summary.todos} isToday={isToday} />
            </div>
          )}

          {/* Chat transcript for past days */}
          {!isToday && summary.chat_messages.length > 0 && (
            <div className="rounded-xl bg-bg-secondary p-4">
              <ChatTranscript messages={summary.chat_messages} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
