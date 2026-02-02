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

  // Scroll to bottom when new messages arrive
  const prevMsgCount = useRef(0);
  useEffect(() => {
    if (messages.length > prevMsgCount.current && prevMsgCount.current > 0) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    }
    prevMsgCount.current = messages.length;
  }, [messages.length]);

  // Also scroll when waiting indicator appears
  useEffect(() => {
    if (isWaiting) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    }
  }, [isWaiting]);

  const hasNoContent =
    historyLoaded &&
    messages.length === 0 &&
    !summaryLoading &&
    !todaySummary?.checkin &&
    !todaySummary?.journal &&
    !todaySummary?.gratitude &&
    todaySummary?.todos.length === 0;

  return (
    <div className="flex min-h-[calc(100vh-3.5rem)] flex-col">
      {/* Scrollable content area */}
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-3xl px-4 py-6 space-y-6">
          {/* Empty state */}
          {hasNoContent && (
            <div className="py-16 text-center">
              <p className="text-lg text-text-secondary">
                What&apos;s on your mind?
              </p>
              <p className="mt-1 text-sm text-text-muted">
                Log meditation, journal, save gratitude, create todos
              </p>
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

          {/* Today's conversation — always visible */}
          {messages.length > 0 && (
            <div>
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-text-muted">
                Conversation
              </h3>
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
            </div>
          )}

          {/* Recent days */}
          <RecentDaysFeed />
        </div>
      </div>

      {/* Chat input pinned at bottom */}
      <div className="shrink-0 border-t border-border bg-bg-primary/95 backdrop-blur-sm">
        <div className="mx-auto max-w-3xl">
          <ChatInput
            onSend={(content) => sendMessage(content)}
            disabled={isWaiting || !isConnected}
          />
          {!isConnected && (
            <div className="px-4 pb-2">
              <p className="text-xs text-accent-primary">Reconnecting...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
