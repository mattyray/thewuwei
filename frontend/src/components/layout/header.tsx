"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { CalendarPicker } from "@/components/daily/calendar-picker";
import { useAuth } from "@/contexts/auth-context";

const navLinks = [
  { href: "/", label: "Today" },
  { href: "/mantras", label: "Mantras" },
  { href: "/settings", label: "Settings" },
];

export function Header() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-20 border-b border-border bg-bg-secondary px-4">
      {/* Main header row */}
      <div className="flex h-14 items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-lg font-bold text-text-primary">
            WuWei
          </Link>

          {/* Desktop nav */}
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

        <div className="flex items-center gap-2">
          <CalendarPicker />
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
        </div>
      </div>

      {/* Mobile nav row — visible on small screens */}
      <nav className="flex items-center gap-1 border-t border-border pb-2 pt-1.5 sm:hidden">
        {navLinks.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`flex-1 rounded-lg py-1.5 text-center text-xs font-medium transition-colors ${
              pathname === link.href
                ? "bg-bg-tertiary text-text-primary"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
