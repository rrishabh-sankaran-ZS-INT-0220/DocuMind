"use client";

import React from "react";

export default function SiteFooter() {
  return (
    <footer className="mx-auto w-full max-w-[1400px] px-4 py-8 text-sm text-[var(--text-muted)]">
      <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
        <div className="flex items-center gap-3">
          <div className="text-sm font-semibold">DocuMind</div>
          <nav className="flex gap-3 text-[var(--text-muted)]">
            <a href="#">Documentation</a>
            <a href="https://github.com" target="_blank" rel="noreferrer">
              GitHub
            </a>
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Contact</a>
          </nav>
        </div>

        <div className="text-[var(--text-muted)]">Version: 0.1.0</div>
      </div>
    </footer>
  );
}
