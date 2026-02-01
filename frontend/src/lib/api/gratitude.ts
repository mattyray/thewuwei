import { apiFetch } from "@/lib/api-client";
import type { GratitudeEntry, PaginatedResponse } from "@/types/api";

export async function getEntries(
  page = 1
): Promise<PaginatedResponse<GratitudeEntry>> {
  return apiFetch<PaginatedResponse<GratitudeEntry>>(
    `/api/gratitude/?page=${page}`
  );
}

export async function getToday(): Promise<GratitudeEntry> {
  return apiFetch<GratitudeEntry>("/api/gratitude/today/");
}

export async function createEntry(data: {
  items: string[];
  date?: string;
}): Promise<GratitudeEntry> {
  return apiFetch<GratitudeEntry>("/api/gratitude/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateEntry(
  id: number,
  data: { items?: string[] }
): Promise<GratitudeEntry> {
  return apiFetch<GratitudeEntry>(`/api/gratitude/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteEntry(id: number): Promise<void> {
  await apiFetch(`/api/gratitude/${id}/`, { method: "DELETE" });
}
