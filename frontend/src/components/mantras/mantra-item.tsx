"use client";

import { FormEvent, useState } from "react";

import type { Mantra } from "@/types/api";

interface MantraItemProps {
  mantra: Mantra;
  isFirst: boolean;
  isLast: boolean;
  onUpdate: (content: string) => void;
  onDelete: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
}

export function MantraItem({
  mantra,
  isFirst,
  isLast,
  onUpdate,
  onDelete,
  onMoveUp,
  onMoveDown,
}: MantraItemProps) {
  const [editing, setEditing] = useState(false);
  const [content, setContent] = useState(mantra.content);

  function handleSave(e: FormEvent) {
    e.preventDefault();
    const trimmed = content.trim();
    if (!trimmed) return;
    onUpdate(trimmed);
    setEditing(false);
  }

  function handleCancel() {
    setContent(mantra.content);
    setEditing(false);
  }

  if (editing) {
    return (
      <form
        onSubmit={handleSave}
        className="rounded-xl border border-accent-primary bg-bg-secondary p-3"
      >
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={2}
          autoFocus
          className="w-full resize-none rounded-lg border border-border bg-bg-primary px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-primary"
        />
        <div className="mt-2 flex gap-2">
          <button
            type="submit"
            className="rounded-lg bg-accent-primary px-3 py-1 text-xs text-white hover:bg-accent-primary/90 cursor-pointer"
          >
            Save
          </button>
          <button
            type="button"
            onClick={handleCancel}
            className="rounded-lg px-3 py-1 text-xs text-text-muted hover:text-text-primary cursor-pointer"
          >
            Cancel
          </button>
        </div>
      </form>
    );
  }

  return (
    <div className="group flex items-start gap-3 rounded-xl border border-border bg-bg-secondary p-3">
      {/* Reorder buttons */}
      <div className="flex flex-col gap-0.5 pt-0.5">
        <button
          onClick={onMoveUp}
          disabled={isFirst}
          className="text-text-muted hover:text-text-primary disabled:opacity-20 cursor-pointer"
          aria-label="Move up"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 16 16"
            fill="currentColor"
            className="h-3.5 w-3.5"
          >
            <path
              fillRule="evenodd"
              d="M8 3.5a.75.75 0 01.53.22l3.25 3.25a.75.75 0 01-1.06 1.06L8 5.31 5.28 8.03a.75.75 0 01-1.06-1.06l3.25-3.25A.75.75 0 018 3.5z"
              clipRule="evenodd"
            />
          </svg>
        </button>
        <button
          onClick={onMoveDown}
          disabled={isLast}
          className="text-text-muted hover:text-text-primary disabled:opacity-20 cursor-pointer"
          aria-label="Move down"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 16 16"
            fill="currentColor"
            className="h-3.5 w-3.5"
          >
            <path
              fillRule="evenodd"
              d="M8 12.5a.75.75 0 01-.53-.22l-3.25-3.25a.75.75 0 111.06-1.06L8 10.69l2.72-2.72a.75.75 0 111.06 1.06l-3.25 3.25a.75.75 0 01-.53.22z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>

      {/* Content */}
      <p className="flex-1 text-sm leading-relaxed text-text-secondary">
        {mantra.content}
      </p>

      {/* Actions */}
      <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
        <button
          onClick={() => setEditing(true)}
          className="rounded px-2 py-1 text-xs text-text-muted hover:text-text-primary cursor-pointer"
        >
          Edit
        </button>
        <button
          onClick={onDelete}
          className="rounded px-2 py-1 text-xs text-text-muted hover:text-error cursor-pointer"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
