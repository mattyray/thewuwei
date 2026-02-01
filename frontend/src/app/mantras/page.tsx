"use client";

import { AuthGuard } from "@/components/auth-guard";
import { Header } from "@/components/layout/header";
import { AddMantraForm } from "@/components/mantras/add-mantra-form";
import { MantraItem } from "@/components/mantras/mantra-item";
import {
  useCreateMantra,
  useDeleteMantra,
  useMantras,
  useReorderMantras,
  useUpdateMantra,
} from "@/hooks/use-mantras";

export default function MantrasPage() {
  const { data, isLoading } = useMantras();
  const createMantra = useCreateMantra();
  const updateMantra = useUpdateMantra();
  const deleteMantra = useDeleteMantra();
  const reorderMantras = useReorderMantras();

  const mantras = data?.results ?? [];

  function handleMoveUp(index: number) {
    if (index === 0) return;
    const newOrder = mantras.map((m) => m.id);
    [newOrder[index - 1], newOrder[index]] = [
      newOrder[index],
      newOrder[index - 1],
    ];
    reorderMantras.mutate(newOrder);
  }

  function handleMoveDown(index: number) {
    if (index >= mantras.length - 1) return;
    const newOrder = mantras.map((m) => m.id);
    [newOrder[index], newOrder[index + 1]] = [
      newOrder[index + 1],
      newOrder[index],
    ];
    reorderMantras.mutate(newOrder);
  }

  return (
    <AuthGuard>
      <Header />
      <main className="mx-auto max-w-xl px-4 py-6">
        <h1 className="mb-6 text-xl font-bold text-text-primary">Mantras</h1>

        <AddMantraForm
          onAdd={(content) => createMantra.mutate({ content })}
          isPending={createMantra.isPending}
        />

        <div className="mt-6 flex flex-col gap-2">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent-primary border-t-transparent" />
            </div>
          ) : mantras.length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">
              No mantras yet. Add your first one above.
            </p>
          ) : (
            mantras.map((mantra, i) => (
              <MantraItem
                key={mantra.id}
                mantra={mantra}
                isFirst={i === 0}
                isLast={i === mantras.length - 1}
                onUpdate={(content) =>
                  updateMantra.mutate({ id: mantra.id, data: { content } })
                }
                onDelete={() => deleteMantra.mutate(mantra.id)}
                onMoveUp={() => handleMoveUp(i)}
                onMoveDown={() => handleMoveDown(i)}
              />
            ))
          )}
        </div>
      </main>
    </AuthGuard>
  );
}
