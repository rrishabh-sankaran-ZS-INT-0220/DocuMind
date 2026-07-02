"use client";

import React from "react";

const steps = [
  "Upload Documents",
  "Extract Text",
  "Generate Embeddings",
  "Vector Database",
  "Semantic Retrieval",
  "LLM Response",
  "Citation-backed Answers",
];

export default function Workflow() {
  return (
    <div className="flex w-full flex-col items-center gap-4">
      <div className="grid w-full grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-7">
        {steps.map((s, i) => (
          <div key={s} className="flex flex-col items-center text-center">
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] px-4 py-3 text-sm font-semibold text-[var(--text)]">
              {s}
            </div>
            {i < steps.length - 1 && (
              <div className="mt-2 hidden sm:block">→</div>
            )}
          </div>
        ))}
      </div>

      {/* Mobile vertical arrows */}
      <div className="sm:hidden mt-2 w-full">
        <ol className="space-y-3">
          {steps.map((s) => (
            <li key={s} className="rounded-2xl border border-[var(--border)] bg-[var(--card)] px-4 py-3 text-sm font-semibold text-[var(--text)]">
              {s}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
