import { apiFetch } from "@/lib/api-client";
import type { PersistedChatMessage } from "@/types/api";

export async function getMessagesByDate(
  date: string
): Promise<PersistedChatMessage[]> {
  return apiFetch<PersistedChatMessage[]>(`/api/chat-messages/${date}/`);
}
