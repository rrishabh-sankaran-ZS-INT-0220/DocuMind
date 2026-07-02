"use client";

import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/context/auth-context";
import { LOGO } from "@/config/logo";

export default function GlobalHeader() {
  const { user, authenticated, logout, login } = useAuth();

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--surface)]">
      <div className="relative mx-auto flex h-20 max-w-6xl items-center justify-center px-4 sm:px-6">
        <div className="flex flex-col items-center text-center">
          <Link href="/" className="inline-flex flex-col items-center gap-1">
            <span className="text-sm font-semibold tracking-tight text-[var(--text)]">
              DocuMind
            </span>
            <span className="text-xs text-[var(--text-muted)]">
              AI workspace for document intelligence
            </span>
          </Link>
        </div>

        <div className="absolute right-4 top-1/2 flex -translate-y-1/2 items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[var(--background)] ring-1 ring-[var(--border)]">
            <Image
              src={LOGO.icon}
              alt={LOGO.alt}
              width={24}
              height={24}
              className="object-contain"
            />
          </div>

          {authenticated ? (
            <button
              type="button"
              onClick={logout}
              className="rounded-full bg-red-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-red-700"
            >
              Sign out
            </button>
          ) : (
            <button
              type="button"
              onClick={login}
              className="rounded-full bg-[var(--accent)] px-4 py-2 text-xs font-semibold text-black transition hover:bg-black/90"
            >
              Sign in
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
