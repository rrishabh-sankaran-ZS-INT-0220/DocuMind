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
    <div className="mx-auto flex w-full max-w-5xl flex-col items-center justify-center py-10">

      {/* Avatar */}

      <div
        className="
          mb-6
          flex
          h-20
          w-20
          items-center
          justify-center
          rounded-full
          border
          border-[var(--border)]
          bg-[var(--surface)]
          text-3xl
          font-semibold
          text-[var(--text)]
        "
      >
        DM
      </div>

      {/* Heading */}

      <h1
        className="
          text-center
          text-6xl
          font-semibold
          tracking-tight
          text-[var(--text)]
        "
      >
        How can I help you today?
      </h1>

      <p
        className="
          mt-5
          max-w-3xl
          text-center
          text-2xl
          leading-10
          text-[var(--text-muted)]
        "
      >
        Upload documents, ask questions, summarize research,
        compare information, and explore your knowledge base with AI.
      </p>

      {/* Cards */}

      <div
        className="
          mt-14
          grid
          w-full
          grid-cols-2
          gap-5
        "
      >
        {suggestions.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.title}
              className="
                rounded-3xl
                border
                border-[var(--border)]
                bg-[var(--surface)]
                p-7
                text-left

                transition-all
                duration-200

                hover:border-[var(--accent)]
                hover:bg-[var(--background)]
              "
            >
              <Icon
                size={28}
                className="mb-5 text-white"
              />

              <h3 className="text-3xl font-semibold text-[var(--text)]">
                {item.title}
              </h3>

              <p
                className="
                  mt-3
                  text-lg
                  leading-8
                  text-[var(--text-muted)]
                "
              >
                {item.description}
              </p>
            </button>
          );
        })}
      </div>

      {/* Footer */}

      <div
        className="
          mt-12
          flex
          items-center
          gap-2
          text-[var(--text-muted)]
        "
      >
        <Sparkles size={16} />

        <span>
          Powered by your private knowledge base
        </span>
      </div>
    </div>
  );
}