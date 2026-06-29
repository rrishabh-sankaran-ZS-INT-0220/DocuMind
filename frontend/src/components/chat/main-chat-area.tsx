"use client";

import React, {
  useMemo,
  useRef,
  useEffect,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import {
  Settings,
  Plus,
  Mic,
  ChevronDown,
  Sparkles,
  MessageSquare,
  Loader2,
} from "lucide-react";

type SourceCitation = {
  document_id: string;
  chunk_text: string;
  score: number;
  page?: number;
  section?: string;
  title?: string;
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  citations?: SourceCitation[];
  confidence?: string;
};

type MainChatAreaProps = {
  question: string;
  setQuestion: (value: string) => void;
  messages: ChatMessage[];
  isAsking: boolean;
  onAsk: () => void | Promise<void>;
  onUpload: (file: File) => void | Promise<void>;
  isUploading?: boolean;
  uploadStatus?: string | null;
  onToggleSidebar?: () => void;
};

const SUGGESTED_PROMPTS: Array<{ title: string; subtitle: string }> = [
  {
    title: "Show me a code snippet",
    subtitle: "Generate a clean example with explanations.",
  },
  {
    title: "Summarize a research paper",
    subtitle: "Highlight contributions, methods, and key findings.",
  },
  {
    title: "Explain a complex concept",
    subtitle: "Use simple language and analogies.",
  },
  {
    title: "Generate flashcards",
    subtitle: "Turn my notes into spaced-repetition cards.",
  },
  {
    title: "Compare two documents",
    subtitle: "Find similarities and differences between sources.",
  },
  {
    title: "Find contradictions",
    subtitle: "Spot conflicting statements in my corpus.",
  },
];

export default function MainChatArea({
  question,
  setQuestion,
  messages,
  isAsking,
  onAsk,
  onUpload,
  isUploading,
  uploadStatus,
  onToggleSidebar,
}: MainChatAreaProps) {
  const router = useRouter();
  const { user } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const hasMessages = messages.length > 0;

  const userInitial = useMemo(
    () =>
      user?.email?.[0]?.toUpperCase() ??
      user?.full_name?.[0]?.toUpperCase() ??
      "U",
    [user]
  );

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isAsking]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onAsk();
    }
  };

  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    onUpload(file);
    e.target.value = "";
  };

  const handleSuggestionClick = (prompt: string) => {
    setQuestion(prompt);
    onAsk();
  };

  return (
    <section className="flex-1 h-screen bg-[#1a1a1a] flex flex-col text-foreground">
      {/* Header bar */}
      <header className="h-14 flex items-center justify-between px-4 border-b border-[#2a2a2a]">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onToggleSidebar}
            className="flex h-9 w-9 items-center justify-center rounded-full bg-[#2a2a2a] text-[#ececec] hover:bg-[#252525] transition-colors duration-150"
            aria-label="Toggle sidebar"
          >
            <MessageSquare className="h-4 w-4" />
          </button>
        </div>

        <div className="flex flex-1 justify-center">
          <button
            type="button"
            className="inline-flex items-center gap-2 bg-[#2a2a2a] hover:bg-[#252525] px-3 py-1.5 rounded-full font-medium text-sm text-[#ececec] transition-colors duration-150"
          >
            <Sparkles className="h-4 w-4 text-[#4f83f1]" />
            <span>gpt-4.1-nano</span>
            <ChevronDown className="h-4 w-4 text-[#8a8a8a]" />
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            className="flex h-9 w-9 items-center justify-center rounded-full border border-[#2a2a2a] bg-transparent text-[#ececec] hover:bg-[#252525] transition-colors duration-150"
            aria-label="Settings"
          >
            <Settings className="h-4 w-4" />
          </button>

          {!user ? (
            <button
              type="button"
              onClick={() => router.push("/login")}
              className="border border-[#3a3a3a] hover:bg-[#252525] rounded-full px-4 py-1.5 text-sm text-[#ececec] transition-colors duration-150"
            >
              Sign In
            </button>
          ) : (
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowUserMenu((prev) => !prev)}
                className="flex h-9 w-9 items-center justify-center rounded-full border border-[#3a3a3a] bg-black/60 text-sm font-semibold text-[#ececec] hover:bg-[#252525] transition-colors duration-150"
                aria-label="User menu"
              >
                {userInitial}
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-56 rounded-lg bg-[#0d0d0d] border border-[#2a2a2a] shadow-lg z-10">
                  <div className="px-3 py-2 border-b border-[#2a2a2a]">
                    <p className="text-[13px] text-[#ececec] truncate">
                      {user?.full_name || user?.email}
                    </p>
                    <p className="text-[12px] text-[#8a8a8a] truncate">
                      {user?.email}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      // Use auth context to clear token
                      const ctx = useAuth() as any;
                      ctx.setAccessToken(null);
                    }}
                    className="w-full text-left px-3 py-2 text-[13px] text-[#ececec] hover:bg-[#1f1f1f]"
                  >
                    Sign out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-[680px] mx-auto px-4 pt-8 pb-6">
          {!hasMessages ? (
            <>
              {/* Welcome state */}
              <div className="flex flex-col items-center text-center">
                <div className="w-10 h-10 rounded-full bg-white text-black text-[14px] font-bold flex items-center justify-center">
                  D
                </div>
                <h1 className="mt-4 text-[18px] font-semibold text-[#ececec]">
                  DocuMind · gpt-4.1-nano
                </h1>
                <p className="mt-1 text-[13px] text-[#8a8a8a]">
                  Ask questions about your documents in a clean, focused workspace.
                </p>
              </div>

              {/* Centered input pill */}
              <div className="mt-8">
                <div className="bg-[#2a2a2a] rounded-3xl px-4 py-3 shadow-lg">
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask a question about your documents..."
                    rows={1}
                    className="w-full bg-transparent resize-none focus:outline-none focus:ring-0 border-none px-1 py-1 text-[#ececec] placeholder:text-[#8a8a8a]"
                    style={{ minHeight: "1.5rem", maxHeight: "8rem" }}
                    disabled={isAsking}
                  />

                  <div className="mt-3 flex justify-between items-center">
                    <button
                      type="button"
                      onClick={handleUploadClick}
                      className="p-1.5 rounded-full hover:bg-[#1f1f1f] text-[#ececec] transition-colors duration-150"
                      aria-label="Upload document"
                    >
                      {isUploading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Plus className="h-4 w-4" />
                      )}
                    </button>

                    <button
                      type="button"
                      onClick={onAsk}
                      disabled={!question.trim() || isAsking}
                      className="flex h-9 w-9 items-center justify-center rounded-full bg-[#4f83f1] text-white hover:bg-[#3b6fd4] disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-150"
                      aria-label="Send"
                    >
                      {isAsking ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Mic className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Suggestions */}
                <div className="mt-4 space-y-1.5">
                  {SUGGESTED_PROMPTS.map((prompt) => (
                    <button
                      key={prompt.title}
                      type="button"
                      onClick={() => handleSuggestionClick(prompt.title)}
                      className="w-full text-left px-3 py-2 rounded-lg text-[13px] text-[#b0b0b0] hover:bg-[#1f1f1f] transition-colors duration-150"
                    >
                      <span className="block">{prompt.title}</span>
                      <span className="block text-[12px] text-[#8a8a8a]">
                        {prompt.subtitle}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <>
              {/* Chat messages */}
              <div className="space-y-4">
                {messages.map((msg, idx) => {
                  const isUser = msg.role === "user";
                  return (
                    <div
                      key={idx}
                      className={`flex gap-3 ${
                        isUser ? "justify-end" : "justify-start"
                      }`}
                    >
                      {!isUser && (
                        <div className="w-7 h-7 rounded-full bg-white text-black text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                          D
                        </div>
                      )}
                      <div className="max-w-[520px] rounded-2xl px-4 py-3 bg-[#1f1f1f] text-[#ececec]">
                        <p className="text-[14px] leading-relaxed whitespace-pre-wrap">
                          {msg.content}
                        </p>

                        {msg.citations && msg.citations.length > 0 && (
                          <div className="mt-3 space-y-2 pt-3 border-t border-[#2a2a2a]">
                            <p className="text-[11px] font-medium text-[#8a8a8a]">
                              Sources
                            </p>
                            {msg.citations.slice(0, 3).map((c, ci) => (
                              <div
                                key={ci}
                                className="rounded-lg bg-[#0d0d0d] px-3 py-2 text-[#b0b0b0]"
                              >
                                {c.title && (
                                  <p className="mb-0.5 font-medium text-[#ececec]">
                                    {c.title}
                                    {c.page != null && ` p. ${c.page}`}
                                    {c.section && ` – ${c.section}`}
                                  </p>
                                )}
                                <p className="line-clamp-2 text-[12px] text-[#8a8a8a]">
                                  {c.chunk_text}
                                </p>
                              </div>
                            ))}
                          </div>
                        )}

                        {msg.confidence && (
                          <p className="mt-2 text-[11px] text-[#8a8a8a]">
                            Confidence: {msg.confidence}
                          </p>
                        )}
                      </div>

                      {isUser && (
                        <div className="w-7 h-7 rounded-full bg-[#4f83f1] text-white text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                          {userInitial}
                        </div>
                      )}
                    </div>
                  );
                })}

                {isAsking && (
                  <div className="flex gap-3">
                    <div className="w-7 h-7 rounded-full bg-white text-black text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                      D
                    </div>
                    <div className="rounded-xl border border-[#2a2a2a] bg-[#0d0d0d] px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        {[0, 1, 2].map((i) => (
                          <span
                            key={i}
                            className="h-1.5 w-1.5 rounded-full bg-[#8a8a8a] animate-bounce"
                            style={{ animationDelay: `${i * 0.15}s` }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {uploadStatus && (
                  <div className="text-[12px] text-[#8a8a8a]">
                    {uploadStatus}
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input pill at bottom of content */}
              <div className="mt-6">
                <div className="bg-[#2a2a2a] rounded-3xl px-4 py-3 shadow-lg">
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask a follow-up question..."
                    rows={1}
                    className="w-full bg-transparent resize-none focus:outline-none focus:ring-0 border-none px-1 py-1 text-[#ececec] placeholder:text-[#8a8a8a]"
                    style={{ minHeight: "1.5rem", maxHeight: "8rem" }}
                    disabled={isAsking}
                  />

                  <div className="mt-3 flex justify-between items-center">
                    <button
                      type="button"
                      onClick={handleUploadClick}
                      className="p-1.5 rounded-full hover:bg-[#1f1f1f] text-[#ececec] transition-colors duration-150"
                      aria-label="Upload document"
                    >
                      {isUploading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Plus className="h-4 w-4" />
                      )}
                    </button>

                    <button
                      type="button"
                      onClick={onAsk}
                      disabled={!question.trim() || isAsking}
                      className="flex h-9 w-9 items-center justify-center rounded-full bg-[#4f83f1] text-white hover:bg-[#3b6fd4] disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-150"
                      aria-label="Send"
                    >
                      {isAsking ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Mic className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={handleFileChange}
      />
    </section>
  );
}