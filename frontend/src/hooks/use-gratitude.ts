import { useQuery } from "@tanstack/react-query";

import { getToday } from "@/lib/api/gratitude";
import { APIError } from "@/lib/api-client";

export function useTodayGratitude() {
  return useQuery({
    queryKey: ["gratitude", "today"],
    queryFn: async () => {
      try {
        return await getToday();
      } catch (err) {
        // 404 means no gratitude entry for today — that's normal
        if (err instanceof APIError && err.status === 404) return null;
        throw err;
      }
    },
  });
}
