import { useQuery } from "@tanstack/react-query";

import { getEntries } from "@/lib/api/journal";

export function useJournalEntries(page = 1) {
  return useQuery({
    queryKey: ["journal", page],
    queryFn: () => getEntries(page),
  });
}
