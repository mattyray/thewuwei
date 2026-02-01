"use client";

import { AuthGuard } from "@/components/auth-guard";
import { HistoryList } from "@/components/history/history-list";
import { Header } from "@/components/layout/header";

export default function HistoryPage() {
  return (
    <AuthGuard>
      <Header />
      <main className="mx-auto max-w-3xl px-4 py-6">
        <h1 className="mb-6 text-xl font-bold text-text-primary">
          Journal History
        </h1>
        <HistoryList />
      </main>
    </AuthGuard>
  );
}
