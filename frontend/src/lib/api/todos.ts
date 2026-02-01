import { apiFetch } from "@/lib/api-client";
import type { PaginatedResponse, Todo } from "@/types/api";

export async function getTodos(
  page = 1
): Promise<PaginatedResponse<Todo>> {
  return apiFetch<PaginatedResponse<Todo>>(`/api/todos/?page=${page}`);
}

export async function createTodo(data: {
  task: string;
  due_date?: string;
}): Promise<Todo> {
  return apiFetch<Todo>("/api/todos/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateTodo(
  id: number,
  data: { task?: string; due_date?: string | null }
): Promise<Todo> {
  return apiFetch<Todo>(`/api/todos/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function completeTodo(id: number): Promise<Todo> {
  return apiFetch<Todo>(`/api/todos/${id}/complete/`, {
    method: "POST",
  });
}

export async function deleteTodo(id: number): Promise<void> {
  await apiFetch(`/api/todos/${id}/`, { method: "DELETE" });
}
