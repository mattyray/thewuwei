import { useQuery } from "@tanstack/react-query";

import { getTodayCheckin } from "@/lib/api/checkins";

export function useCheckin() {
  return useQuery({
    queryKey: ["checkin"],
    queryFn: getTodayCheckin,
  });
}
