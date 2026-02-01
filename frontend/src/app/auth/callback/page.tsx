"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/contexts/auth-context";
import * as authApi from "@/lib/api/auth";

export default function AuthCallbackPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    // After OAuth redirect, the session should already be set by allauth.
    // Just verify we have a user and redirect.
    async function check() {
      try {
        await authApi.getMe();
        router.replace("/");
      } catch {
        router.replace("/login");
      }
    }

    if (!isLoading) {
      if (user) {
        router.replace("/");
      } else {
        check();
      }
    }
  }, [user, isLoading, router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent-primary border-t-transparent" />
    </div>
  );
}
