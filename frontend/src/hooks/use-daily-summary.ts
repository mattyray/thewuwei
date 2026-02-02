import { useQuery } from "@tanstack/react-query";

import {
  getDailySummary,
  getRecentSummaries,
  getTodaySummary,
} from "@/lib/api/daily";

export function useTodaySummary() {
  return useQuery({
    queryKey: ["daily", "today"],
    queryFn: getTodaySummary,
  });
}

export function useDailySummary(date: string) {
  return useQuery({
    queryKey: ["daily", date],
    queryFn: () => getDailySummary(date),
    enabled: !!date,
  });
}

export function useRecentSummaries(days = 5) {
  return useQuery({
    queryKey: ["daily", "recent", days],
    queryFn: () => getRecentSummaries(days),
  });
}
