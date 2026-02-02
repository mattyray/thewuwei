import { apiFetch } from "@/lib/api-client";
import type { DailySummary } from "@/types/api";

export async function getDailySummary(date: string): Promise<DailySummary> {
  return apiFetch<DailySummary>(`/api/daily/${date}/`);
}

export async function getTodaySummary(): Promise<DailySummary> {
  return apiFetch<DailySummary>("/api/daily/today/");
}

export async function getRecentSummaries(
  days = 5
): Promise<DailySummary[]> {
  return apiFetch<DailySummary[]>(`/api/daily/recent/?days=${days}`);
}
