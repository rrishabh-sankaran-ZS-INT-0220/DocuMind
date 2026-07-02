"use client";

import React from "react";

const cases = [
  "Academic Research",
  "Enterprise Knowledge Base",
  "Legal Documents",
  "Technical Documentation",
  "Research Papers",
  "Company SOPs",
  "Business Reports",
  "Meeting Notes",
];

export default function UseCases() {
  return (
    <div className="grid w-full grid-cols-2 gap-3 sm:grid-cols-4">
      {cases.map((c) => (
        <div key={c} className="rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--text-muted)]">
          {c}
        </div>
      ))}
    </div>
  );
}
