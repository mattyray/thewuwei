import { apiFetch } from "@/lib/api-client";
import type { Mantra, PaginatedResponse } from "@/types/api";

export async function getMantras(
  page = 1
): Promise<PaginatedResponse<Mantra>> {
  return apiFetch<PaginatedResponse<Mantra>>(`/api/mantras/?page=${page}`);
}

export async function createMantra(data: {
  content: string;
}): Promise<Mantra> {
  return apiFetch<Mantra>("/api/mantras/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateMantra(
  id: number,
  data: { content?: string; order?: number }
): Promise<Mantra> {
  return apiFetch<Mantra>(`/api/mantras/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteMantra(id: number): Promise<void> {
  await apiFetch(`/api/mantras/${id}/`, { method: "DELETE" });
}

export async function reorderMantras(order: number[]): Promise<void> {
  await apiFetch("/api/mantras/reorder/", {
    method: "POST",
    body: JSON.stringify({ order }),
  });
}
