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
      viewport.scrollHeight - viewport.scrollTop - viewport.clientHeight;

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
        relative
        flex
        h-[100dvh]
        min-h-0
        flex-1
        flex-col
        overflow-hidden
        bg-[#212121]
      "
    >
      {/* ================= Conversation ================= */}

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
            px-8
            pt-10
            pb-56
          "
        >
          {isEmpty ? (
            <div
              className="
                flex
                min-h-[calc(100dvh-220px)]
                items-center
                justify-center
                -translate-y-6
              "
            >
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
            border-[#404040]
            bg-[#2B2B2B]
            text-white
            shadow-lg
            transition-all
            duration-200
            hover:bg-[#383838]
          "
        >
          ↓
        </button>
      )}

      {/* ================= Composer ================= */}

      <div
        className="
          sticky
          bottom-0
          z-20
          bg-[#212121]/95
          backdrop-blur-xl
          before:absolute
          before:left-0
          before:right-0
          before:top-0
          before:h-8
          before:bg-gradient-to-t
          before:from-[#212121]
          before:to-transparent
        "
      >
        <div
          className="
            mx-auto
            w-full
            max-w-4xl
            px-8
            pb-8
            pt-4
          "
        >
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