"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";

import type { ChatMessage } from "@/types/api";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

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

      const ws = new WebSocket(`${WS_URL}/ws/chat/`);

      ws.onopen = () => {
        // Guard against stale WS (Strict Mode closes the first one)
        if (wsRef.current !== ws) return;
        setIsConnected(true);
        retries = 0;
      };

      ws.onmessage = (event) => {
        if (wsRef.current !== ws) return;
        const data = JSON.parse(event.data);
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
      };

      ws.onclose = () => {
        // Only handle close if this is still the active WS.
        // Prevents stale WS1.onclose from clobbering active WS2.
        if (wsRef.current !== ws) return;
        setIsConnected(false);
        wsRef.current = null;
        if (unmounted) return;
        const delay = Math.min(1000 * 2 ** retries, 30000);
        retries += 1;
        reconnectTimeout = setTimeout(connect, delay);
      };

      ws.onerror = () => {
        ws.close();
      };

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
