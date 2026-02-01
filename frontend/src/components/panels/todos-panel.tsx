"use client";

import { FormEvent, useState } from "react";

import { Card } from "@/components/ui/card";
import { useCompleteTodo, useCreateTodo, useTodos } from "@/hooks/use-todos";

export function TodosPanel() {
  const { data, isLoading } = useTodos();
  const createTodo = useCreateTodo();
  const completeTodo = useCompleteTodo();
  const [newTask, setNewTask] = useState("");

  const pending =
    data?.results.filter((t) => !t.completed).slice(0, 7) ?? [];

  function handleAdd(e: FormEvent) {
    e.preventDefault();
    const trimmed = newTask.trim();
    if (!trimmed) return;
    createTodo.mutate({ task: trimmed });
    setNewTask("");
  }

  return (
    <Card title="Todos">
      {isLoading ? (
        <p className="text-sm text-text-muted">Loading...</p>
      ) : pending.length === 0 ? (
        <p className="text-sm text-text-muted">All clear</p>
      ) : (
        <ul className="flex flex-col gap-1">
          {pending.map((todo) => (
            <li key={todo.id} className="flex items-start gap-2 py-0.5">
              <button
                onClick={() => completeTodo.mutate(todo.id)}
                className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border border-border transition-colors hover:border-success cursor-pointer"
                aria-label={`Complete: ${todo.task}`}
              />
              <span className="text-sm text-text-primary leading-snug">
                {todo.task}
              </span>
            </li>
          ))}
        </ul>
      )}

      <form onSubmit={handleAdd} className="mt-3 flex gap-2">
        <input
          value={newTask}
          onChange={(e) => setNewTask(e.target.value)}
          placeholder="Add a todo..."
          className="flex-1 rounded-lg border border-border bg-bg-primary px-2.5 py-1.5 text-xs text-text-primary placeholder:text-text-muted outline-none focus:border-accent-primary"
        />
        <button
          type="submit"
          disabled={!newTask.trim()}
          className="rounded-lg bg-bg-tertiary px-2.5 py-1.5 text-xs text-text-primary transition-colors hover:bg-bg-tertiary/80 disabled:opacity-40 cursor-pointer"
        >
          Add
        </button>
      </form>
    </Card>
  );
}
