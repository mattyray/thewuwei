import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import * as todosApi from "@/lib/api/todos";

export function useTodos() {
  return useQuery({
    queryKey: ["todos"],
    queryFn: () => todosApi.getTodos(),
  });
}

export function useCreateTodo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: todosApi.createTodo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["todos"] });
    },
  });
}

export function useCompleteTodo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: todosApi.completeTodo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["todos"] });
    },
  });
}

export function useDeleteTodo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: todosApi.deleteTodo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["todos"] });
    },
  });
}
