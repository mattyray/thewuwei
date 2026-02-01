"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "@/contexts/auth-context";

const navLinks = [
  { href: "/", label: "Dashboard" },
  { href: "/history", label: "History" },
  { href: "/mantras", label: "Mantras" },
  { href: "/settings", label: "Settings" },
];

export function Header() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-bg-secondary px-4">
      <div className="flex items-center gap-6">
        <Link href="/" className="text-lg font-bold text-text-primary">
          WuWei
        </Link>

        <nav className="hidden items-center gap-1 sm:flex">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`rounded-lg px-3 py-1.5 text-sm transition-colors ${
                pathname === link.href
                  ? "bg-bg-tertiary text-text-primary"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>

      {user && (
        <div className="flex items-center gap-3">
          <span className="hidden text-sm text-text-muted sm:block">
            {user.email}
          </span>
          <button
            onClick={logout}
            className="rounded-lg px-3 py-1.5 text-sm text-text-secondary transition-colors hover:text-text-primary cursor-pointer"
          >
            Logout
          </button>
        </div>
      )}
    </header>
  );
}
