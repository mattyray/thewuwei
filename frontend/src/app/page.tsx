"use client";

import { AuthGuard } from "@/components/auth-guard";
import { Dashboard } from "@/components/dashboard";
import { Header } from "@/components/layout/header";

export default function Home() {
  return (
    <AuthGuard>
      <Header />
      <Dashboard />
    </AuthGuard>
  );
}
