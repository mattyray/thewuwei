"use client";

import { AuthGuard } from "@/components/auth-guard";
import { DailyPage } from "@/components/daily-page";
import { Header } from "@/components/layout/header";

export default function Home() {
  return (
    <AuthGuard>
      <Header />
      <DailyPage />
    </AuthGuard>
  );
}
