"use client";

import { useEffect, useRef } from "react";

import { useChat } from "@/hooks/use-chat";

import { ChatInput } from "./chat-input";
import { ChatMessageBubble } from "./chat-message";

export function Chat() {
  const { messages, sendMessage, isConnected, isWaiting } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isWaiting]);

  return (
    <div className="flex h-full flex-col">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <p className="text-lg font-medium text-text-secondary">
                What&apos;s on your mind?
              </p>
              <p className="mt-1 text-sm text-text-muted">
                Log meditation, journal, save gratitude, create todos...
              </p>
            </div>
          </div>
        )}

        <div className="flex flex-col gap-3">
          {messages.map((msg, i) => (
            <ChatMessageBubble key={i} message={msg} />
          ))}

          {isWaiting && (
            <div className="flex justify-start">
              <div className="rounded-2xl rounded-bl-md bg-bg-secondary px-4 py-3">
                <div className="flex gap-1">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-text-muted [animation-delay:0ms]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-text-muted [animation-delay:150ms]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-text-muted [animation-delay:300ms]" />
                </div>
              </div>
            </div>
          )}
        </div>

        <div ref={bottomRef} />
      </div>

      {/* Connection status */}
      {!isConnected && (
        <div className="px-4 py-1 text-center text-xs text-text-muted">
          Reconnecting...
        </div>
      )}

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={isWaiting || !isConnected} />
    </div>
  );
}
