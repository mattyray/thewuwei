import { apiFetch } from "@/lib/api-client";
import type { DailyCheckin } from "@/types/api";

export async function getTodayCheckin(): Promise<DailyCheckin> {
  return apiFetch<DailyCheckin>("/api/checkins/today/");
}

export async function logMeditation(
  durationMinutes?: number
): Promise<DailyCheckin> {
  return apiFetch<DailyCheckin>("/api/checkins/meditation/", {
    method: "POST",
    body: JSON.stringify(
      durationMinutes != null ? { duration_minutes: durationMinutes } : {}
    ),
  });
}
