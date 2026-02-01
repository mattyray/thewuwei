import { apiFetch } from "@/lib/api-client";
import type { JournalEntry, PaginatedResponse } from "@/types/api";

export async function getEntries(
  page = 1
): Promise<PaginatedResponse<JournalEntry>> {
  return apiFetch<PaginatedResponse<JournalEntry>>(
    `/api/journal/?page=${page}`
  );
}

export async function getToday(): Promise<JournalEntry> {
  return apiFetch<JournalEntry>("/api/journal/today/");
}

export async function getByDate(date: string): Promise<JournalEntry> {
  return apiFetch<JournalEntry>(`/api/journal/${date}/`);
}

export async function createEntry(data: {
  content: string;
  date?: string;
}): Promise<JournalEntry> {
  return apiFetch<JournalEntry>("/api/journal/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateEntry(
  id: number,
  data: { content?: string }
): Promise<JournalEntry> {
  return apiFetch<JournalEntry>(`/api/journal/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteEntry(id: number): Promise<void> {
  await apiFetch(`/api/journal/${id}/`, { method: "DELETE" });
}
