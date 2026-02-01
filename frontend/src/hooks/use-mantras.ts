import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import * as mantrasApi from "@/lib/api/mantras";

export function useMantras() {
  return useQuery({
    queryKey: ["mantras"],
    queryFn: () => mantrasApi.getMantras(),
  });
}

export function useCreateMantra() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: mantrasApi.createMantra,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mantras"] });
    },
  });
}

export function useUpdateMantra() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: { content?: string; order?: number } }) =>
      mantrasApi.updateMantra(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mantras"] });
    },
  });
}

export function useDeleteMantra() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: mantrasApi.deleteMantra,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mantras"] });
    },
  });
}

export function useReorderMantras() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: mantrasApi.reorderMantras,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mantras"] });
    },
  });
}
