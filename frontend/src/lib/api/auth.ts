import { apiFetch } from "@/lib/api-client";
import type { User } from "@/types/api";

export async function getCSRF(): Promise<void> {
  await apiFetch<{ csrfToken: string }>("/api/auth/csrf/");
}

export async function login(email: string, password: string): Promise<User> {
  return apiFetch<User>("/api/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function register(
  email: string,
  password: string,
  passwordConfirm: string
): Promise<User> {
  return apiFetch<User>("/api/auth/register/", {
    method: "POST",
    body: JSON.stringify({
      email,
      password,
      password_confirm: passwordConfirm,
    }),
  });
}

export async function logout(): Promise<void> {
  await apiFetch("/api/auth/logout/", { method: "POST" });
}

export async function getMe(): Promise<User> {
  return apiFetch<User>("/api/auth/me/");
}

export async function updateMe(
  data: Partial<Pick<User, "timezone" | "daily_reminder_time" | "reminder_enabled">>
): Promise<User> {
  return apiFetch<User>("/api/auth/me/", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}
