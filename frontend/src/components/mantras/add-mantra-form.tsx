"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";

interface AddMantraFormProps {
  onAdd: (content: string) => void;
  isPending: boolean;
}

export function AddMantraForm({ onAdd, isPending }: AddMantraFormProps) {
  const [content, setContent] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = content.trim();
    if (!trimmed) return;
    onAdd(trimmed);
    setContent("");
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Add a new mantra..."
        className="flex-1 rounded-lg border border-border bg-bg-secondary px-3 py-2 text-sm text-text-primary placeholder:text-text-muted outline-none focus:border-accent-primary"
      />
      <Button type="submit" disabled={isPending || !content.trim()}>
        Add
      </Button>
    </form>
  );
}
