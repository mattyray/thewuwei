"use client";

import { useState } from "react";

import { ChatMessageBubble } from "@/components/chat/chat-message";
import type { PersistedChatMessage } from "@/types/api";

interface ChatTranscriptProps {
  messages: PersistedChatMessage[];
}

export function ChatTranscript({ messages }: ChatTranscriptProps) {
  const [expanded, setExpanded] = useState(false);

  if (messages.length === 0) return null;

  return (
    <div>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xs text-accent-primary hover:underline cursor-pointer"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className={`h-3.5 w-3.5 transition-transform ${
            expanded ? "rotate-90" : ""
          }`}
        >
          <path
            fillRule="evenodd"
            d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
            clipRule="evenodd"
          />
        </svg>
        View conversation ({messages.length} message{messages.length !== 1 ? "s" : ""})
      </button>
      {expanded && (
        <div className="mt-3 space-y-3">
          {messages.map((msg) => (
            <ChatMessageBubble
              key={msg.id}
              message={{ role: msg.role, content: msg.content }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
