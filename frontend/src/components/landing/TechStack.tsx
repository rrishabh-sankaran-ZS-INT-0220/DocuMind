"use client";

import React from "react";

const groups = [
  { title: "Frontend", items: ["Next.js", "React", "Tailwind CSS"] },
  { title: "Backend", items: ["FastAPI", "Python"] },
  { title: "AI", items: ["Sentence Transformers", "Transformers", "RAG Pipeline"] },
  { title: "Database", items: ["PostgreSQL", "pgvector"] },
  { title: "Authentication", items: ["Google OAuth", "JWT"] },
];

export default function TechStack() {
  return (
    <div className="grid w-full grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {groups.map((g) => (
        <div key={g.title} className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--text-muted)]">{g.title}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {g.items.map((i) => (
              <span key={i} className="rounded-md border border-[var(--border)] bg-[var(--surface)] px-3 py-1 text-sm text-[var(--text-muted)]">
                {i}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
