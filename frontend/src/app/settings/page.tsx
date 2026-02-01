"use client";

import { AuthGuard } from "@/components/auth-guard";
import { Header } from "@/components/layout/header";
import { NotificationsSection } from "@/components/settings/notifications-section";
import { ProfileSection } from "@/components/settings/profile-section";

export default function SettingsPage() {
  return (
    <AuthGuard>
      <Header />
      <main className="mx-auto max-w-xl px-4 py-6">
        <h1 className="mb-6 text-xl font-bold text-text-primary">Settings</h1>
        <div className="flex flex-col gap-4">
          <ProfileSection />
          <NotificationsSection />
        </div>
      </main>
    </AuthGuard>
  );
}
