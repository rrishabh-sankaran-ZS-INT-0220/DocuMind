"use client";

import {
  FileText,
  FileSearch,
  Files,
  Sparkles,
} from "lucide-react";

const suggestions = [
  {
    icon: FileText,
    title: "Summarize",
    description:
      "Generate a concise summary of a document.",
  },
  {
    icon: Sparkles,
    title: "Explain",
    description:
      "Explain difficult concepts in simple language.",
  },
  {
    icon: Files,
    title: "Compare",
    description:
      "Compare multiple documents and identify differences.",
  },
  {
    icon: FileSearch,
    title: "Extract",
    description:
      "Find key facts, entities and important information.",
  },
];

export function EmptyState() {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col items-center justify-center py-4">
      {/* Heading */}

      <h1
        className="
          mt-25
          text-center
          text-6xl
          font-semibold
          tracking-tight
          text-[var(--text)]
        "
      >
        How can I help you today?
      </h1>
    </div>
  );
}