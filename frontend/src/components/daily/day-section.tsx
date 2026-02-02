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

  return (
    <div className="border-t border-border pt-4">
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
        <div className="mt-3 space-y-5">
          <MeditationRow checkin={summary.checkin} />
          <GratitudeSection gratitude={summary.gratitude} />
          <JournalSection journal={summary.journal} />
          <TodosSection todos={summary.todos} isToday={isToday} />
          {!isToday && (
            <ChatTranscript messages={summary.chat_messages} />
          )}
        </div>
      )}
    </div>
  );
}
