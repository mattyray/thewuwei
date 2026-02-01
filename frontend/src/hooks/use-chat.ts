"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";

import type { ChatMessage } from "@/types/api";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

function createWebSocket(
  onMessage: (data: { type: string; content: string }) => void,
  onOpen: () => void,
  onClose: () => void
): WebSocket {
  const ws = new WebSocket(`${WS_URL}/ws/chat/`);
  ws.onopen = onOpen;
  ws.onmessage = (event) => onMessage(JSON.parse(event.data));
  ws.onclose = onClose;
  ws.onerror = () => ws.close();
  return ws;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isWaiting, setIsWaiting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    let retries = 0;
    let reconnectTimeout: ReturnType<typeof setTimeout>;
    let unmounted = false;

    function connect() {
      if (unmounted) return;

      const ws = createWebSocket(
        (data) => {
          if (data.type === "complete") {
            setMessages((prev) => [
              ...prev,
              { role: "assistant", content: data.content },
            ]);
            setIsWaiting(false);

            queryClient.invalidateQueries({ queryKey: ["checkin"] });
            queryClient.invalidateQueries({ queryKey: ["todos"] });
            queryClient.invalidateQueries({ queryKey: ["mantras"] });
            queryClient.invalidateQueries({ queryKey: ["gratitude"] });
          }
        },
        () => {
          setIsConnected(true);
          retries = 0;
        },
        () => {
          setIsConnected(false);
          wsRef.current = null;
          if (unmounted) return;
          const delay = Math.min(1000 * 2 ** retries, 30000);
          retries += 1;
          reconnectTimeout = setTimeout(connect, delay);
        }
      );

      wsRef.current = ws;
    }

    connect();

    return () => {
      unmounted = true;
      clearTimeout(reconnectTimeout);
      wsRef.current?.close();
    };
  }, [queryClient]);

  const sendMessage = useCallback((content: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    setMessages((prev) => [...prev, { role: "user", content }]);
    setIsWaiting(true);

    wsRef.current.send(JSON.stringify({ type: "message", content }));
  }, []);

  return { messages, sendMessage, isConnected, isWaiting };
}
