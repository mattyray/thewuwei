"use client";

import { useEffect, useRef, useState } from "react";

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
  const [chatOpen, setChatOpen] = useState(false);

  // Auto-open chat and scroll when new messages arrive from this session
  const prevMsgCount = useRef(0);
  useEffect(() => {
    if (messages.length > prevMsgCount.current && prevMsgCount.current > 0) {
      // New message arrived during this session — open chat and scroll
      setChatOpen(true);
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    }
    prevMsgCount.current = messages.length;
  }, [messages.length]);

  // Also scroll when waiting indicator appears
  useEffect(() => {
    if (isWaiting && chatOpen) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    }
  }, [isWaiting, chatOpen]);

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

          {/* Today's structured sections — always first */}
          {todaySummary && (
            <DaySection
              summary={todaySummary}
              isToday={true}
              defaultExpanded={true}
            />
          )}

          {/* Today's conversation — collapsible */}
          {messages.length > 0 && (
            <div className="border-t border-border pt-4">
              <button
                onClick={() => setChatOpen(!chatOpen)}
                className="flex w-full items-center gap-2 text-left"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  className={`h-4 w-4 shrink-0 text-text-muted transition-transform ${
                    chatOpen ? "rotate-90" : ""
                  }`}
                >
                  <path
                    fillRule="evenodd"
                    d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-sm font-semibold uppercase tracking-wider text-text-muted">
                  Conversation
                </span>
                <span className="text-xs text-text-muted">
                  ({messages.length} message{messages.length !== 1 ? "s" : ""})
                </span>
              </button>

              {chatOpen && (
                <div className="mt-3 space-y-3">
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
            onSend={(content) => {
              setChatOpen(true);
              sendMessage(content);
            }}
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
