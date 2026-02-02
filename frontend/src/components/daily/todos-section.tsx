"use client";

import { FormEvent, useState } from "react";

import { useCompleteTodo, useCreateTodo } from "@/hooks/use-todos";
import type { Todo } from "@/types/api";

interface TodosSectionProps {
  todos: Todo[];
  isToday: boolean;
}

export function TodosSection({ todos, isToday }: TodosSectionProps) {
  const createTodo = useCreateTodo();
  const completeTodo = useCompleteTodo();
  const [newTask, setNewTask] = useState("");

  function handleAdd(e: FormEvent) {
    e.preventDefault();
    const trimmed = newTask.trim();
    if (!trimmed) return;
    createTodo.mutate({ task: trimmed });
    setNewTask("");
  }

  if (!isToday && todos.length === 0) return null;

  return (
    <div>
      <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-text-muted">
        Todos
      </h4>
      {todos.length === 0 ? (
        <p className="text-sm text-text-muted">No todos yet</p>
      ) : (
        <ul className="space-y-1">
          {todos.map((todo) => (
            <li key={todo.id} className="flex items-start gap-2 py-0.5">
              {isToday ? (
                <button
                  onClick={() => completeTodo.mutate(todo.id)}
                  className={`mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border transition-colors cursor-pointer ${
                    todo.completed
                      ? "border-success bg-success/20"
                      : "border-border hover:border-success"
                  }`}
                  aria-label={`Complete: ${todo.task}`}
                >
                  {todo.completed && (
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      className="h-3 w-3 text-success"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </button>
              ) : (
                <div
                  className={`mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border ${
                    todo.completed
                      ? "border-success bg-success/20"
                      : "border-border"
                  }`}
                >
                  {todo.completed && (
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      className="h-3 w-3 text-success"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </div>
              )}
              <span
                className={`text-sm leading-snug ${
                  todo.completed
                    ? "text-text-muted line-through"
                    : "text-text-primary"
                }`}
              >
                {todo.task}
              </span>
            </li>
          ))}
        </ul>
      )}

      {isToday && (
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
      )}
    </div>
  );
}
