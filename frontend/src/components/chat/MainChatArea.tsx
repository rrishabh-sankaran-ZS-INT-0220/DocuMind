"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { ChatComposer } from "./composer/ChatComposer";
import { EmptyState } from "./empty/EmptyState";
import { MessageViewport } from "./messages/MessageViewport";
import { TypingIndicator } from "./messages/TypingIndicator";

export type SourceCitation = {
  document_id: string;
  chunk_text: string;
  score: number;
  page?: number;
  section?: string;
  title?: string;
};

export type ChatMessage = {
  role: "user" | "assistant" | "system";
  content: string;
  citations?: SourceCitation[];
  confidence?: string;
};

interface MainChatAreaProps {
  question: string;
  setQuestion: (value: string) => void;

  messages: ChatMessage[];

  isAsking: boolean;

  onAsk: () => void;

  onUpload: (file: File) => void;

  isUploading: boolean;

  uploadStatus?: string;

  onToggleSidebar: () => void;
}

export default function MainChatArea({
  question,
  setQuestion,
  messages,
  isAsking,
  onAsk,
  onUpload,
  isUploading,
  uploadStatus,
}: MainChatAreaProps) {
  const viewportRef = useRef<HTMLDivElement>(null);

  const [showScrollButton, setShowScrollButton] = useState(false);

  const isEmpty = messages.length === 0;

  useEffect(() => {
    const viewport = viewportRef.current;

    if (!viewport) return;

    viewport.scrollTo({
      top: viewport.scrollHeight,
      behavior: messages.length > 2 ? "smooth" : "instant",
    });
  }, [messages, isAsking]);

  const handleScroll = useCallback(() => {
    const viewport = viewportRef.current;

    if (!viewport) return;

    const distance =
      viewport.scrollHeight -
      viewport.scrollTop -
      viewport.clientHeight;

    setShowScrollButton(distance > 300);
  }, []);

  const scrollToBottom = () => {
    viewportRef.current?.scrollTo({
      top: viewportRef.current.scrollHeight,
      behavior: "smooth",
    });
  };

  return (
    <main
      className="
        flex
        min-h-0
        flex-1
        flex-col
        overflow-hidden
        bg-[var(--background)]
      "
    >
      {/* ================= Messages ================= */}

      <div
        ref={viewportRef}
        onScroll={handleScroll}
        className="
          flex-1
          overflow-y-auto
          overflow-x-hidden
        "
      >
        <div
          className="
            mx-auto
            w-full
            max-w-4xl
            px-6
            pt-10
            pb-12
          "
        >
          {isEmpty ? (
            <div className="min-h-full">
              <EmptyState />
            </div>
          ) : (
            <>
              <MessageViewport messages={messages} />

              {isAsking && (
                <div className="mt-6">
                  <TypingIndicator />
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* ================= Scroll Button ================= */}

      {showScrollButton && (
        <button
          onClick={scrollToBottom}
          className="
            absolute
            bottom-40
            right-8
            z-30

            flex
            h-11
            w-11
            items-center
            justify-center

            rounded-full

            border
            border-[var(--border)]

            bg-[var(--surface)]

            text-[var(--text)]

            shadow-lg

            transition-all
            duration-200

            hover:bg-[var(--card)]
          "
        >
          ↓
        </button>
      )}

      {/* ================= Composer ================= */}

      <div className="shrink-0 border-t border-[var(--border)] bg-[var(--background)]">
        <div className="mx-auto w-full max-w-4xl px-6 py-6">
          <ChatComposer
            question={question}
            setQuestion={setQuestion}
            isAsking={isAsking}
            onAsk={onAsk}
            onUpload={onUpload}
            isUploading={isUploading}
            uploadStatus={uploadStatus}
          />
        </div>
      </div>
    </main>
  );
}