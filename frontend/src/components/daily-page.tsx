"use client";

import { useEffect, useRef } from "react";

import { ChatInput } from "@/components/chat/chat-input";
import { ChatMessageBubble } from "@/components/chat/chat-message";
import { DaySection } from "@/components/daily/day-section";
import { RecentDaysFeed } from "@/components/daily/recent-days-feed";
import { useChat } from "@/hooks/use-chat";
import { useTodaySummary } from "@/hooks/use-daily-summary";

export function DailyPage() {
  const { messages, sendMessage, isConnected, isWaiting, historyLoaded } =
    useChat();
  const { data: todaySummary, isLoading: summaryLoading } = useTodaySummary();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of chat when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, isWaiting]);

  const showEmptyState =
    historyLoaded && messages.length === 0 && !summaryLoading;

  return (
    <div className="min-h-[calc(100vh-3.5rem)]">
      {/* Sticky chat input */}
      <div className="sticky top-14 z-10 border-b border-border bg-bg-primary/95 backdrop-blur-sm">
        <div className="mx-auto max-w-3xl">
          <ChatInput
            onSend={sendMessage}
            disabled={isWaiting || !isConnected}
          />
          {!isConnected && (
            <div className="px-4 pb-2">
              <p className="text-xs text-accent-primary">Reconnecting...</p>
            </div>
          )}
        </div>
      </div>

      <div className="mx-auto max-w-3xl px-4 py-6 space-y-6">
        {/* Today's live chat messages */}
        {showEmptyState && (
          <div className="py-12 text-center">
            <p className="text-lg text-text-secondary">
              What&apos;s on your mind?
            </p>
            <p className="mt-1 text-sm text-text-muted">
              Log meditation, journal, save gratitude, create todos
            </p>
          </div>
        )}

        {messages.length > 0 && (
          <div className="space-y-3">
            {messages.map((msg, i) => (
              <ChatMessageBubble key={i} message={msg} />
            ))}
            {isWaiting && (
              <div className="flex justify-start">
                <div className="rounded-2xl rounded-bl-md bg-bg-secondary px-4 py-2.5">
                  <div className="flex gap-1">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-text-muted [animation-delay:-0.3s]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-text-muted [animation-delay:-0.15s]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-text-muted" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Today's structured sections */}
        {todaySummary && (
          <DaySection
            summary={todaySummary}
            isToday={true}
            defaultExpanded={true}
          />
        )}

        {/* Recent days */}
        <RecentDaysFeed />
      </div>
    </div>
  );
}
