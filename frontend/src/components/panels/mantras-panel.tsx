"use client";

import Link from "next/link";

import { Card } from "@/components/ui/card";
import { useMantras } from "@/hooks/use-mantras";

export function MantrasPanel() {
  const { data, isLoading } = useMantras();

  const mantras = data?.results ?? [];

  return (
    <Card title="Mantras">
      {isLoading ? (
        <p className="text-sm text-text-muted">Loading...</p>
      ) : mantras.length === 0 ? (
        <p className="text-sm text-text-muted">
          No mantras yet. Add one via chat or the{" "}
          <Link href="/mantras" className="text-accent-primary hover:underline">
            mantras page
          </Link>
          .
        </p>
      ) : (
        <ul className="flex flex-col gap-2">
          {mantras.slice(0, 5).map((mantra) => (
            <li
              key={mantra.id}
              className="text-sm leading-relaxed text-text-secondary"
            >
              {mantra.content}
            </li>
          ))}
          {mantras.length > 5 && (
            <li className="text-xs text-text-muted">
              +{mantras.length - 5} more
            </li>
          )}
        </ul>
      )}

      <Link
        href="/mantras"
        className="mt-3 block text-xs text-accent-primary hover:underline"
      >
        Manage mantras
      </Link>
    </Card>
  );
}
