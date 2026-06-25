"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { apiClient } from "@/lib/api";
import { useCollections, useQASessions } from "@/lib/hooks";
import type { Collection, QASession } from "@/lib/hooks";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type SourceCitation = {
  document_id: string;
  chunk_text: string;
  score: number;
  page?: number;
  section?: string;
  title?: string;
};

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  citations?: SourceCitation[];
  confidence?: string;
};

export default function AskPage() {
  const router = useRouter();
  const { user, loading } = useAuth();

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isAsking, setIsAsking] = useState(false);
  const [askError, setAskError] = useState<string | null>(null);
  const [selectedCollectionId, setSelectedCollectionId] = useState<string | null>(null);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: collections = [] } = useCollections();
  const { data: sessions = [], refetch: refetchSessions } = useQASessions();

  // Auth guard
  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  // Scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isAsking]);

  // -- Ask --------------------------------------------------------------
  const handleAsk = useCallback(async () => {
    const q = question.trim();
    if (!q || isAsking) return;

    setQuestion("");
    setAskError(null);
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setIsAsking(true);

    try {
      const { data } = await apiClient.post("/qa/ask", {
        question: q,
        session_id: activeSessionId ?? undefined,
        collection_id: selectedCollectionId ?? undefined,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer ?? "",
          citations: Array.isArray(data.citations) ? data.citations : [],
          confidence: data.confidence,
        },
      ]);

      if (data.session_id && !activeSessionId) {
        setActiveSessionId(data.session_id);
      }

      refetchSessions();
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setAskError(msg);
    } finally {
      setIsAsking(false);
    }
  }, [question, isAsking, activeSessionId, selectedCollectionId, refetchSessions]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  // -- Upload -----------------------------------------------------------
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus("Uploading...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const { data } = await apiClient.post("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setUploadStatus("Processing...");
      let attempts = 0;

      const poll = setInterval(async () => {
        attempts++;
        try {
          const res = await apiClient.get("/documents/" + data.id + "/status");
          const s = res.data;
          if (s.status === "ready") {
            clearInterval(poll);
            setUploadStatus("Ready: " + file.name);
            setTimeout(() => setUploadStatus(null), 3000);
          } else if (s.status === "failed") {
            clearInterval(poll);
            setUploadStatus("Failed: " + (s.error_message ?? "unknown error"));
          } else if (attempts > 30) {
            clearInterval(poll);
            setUploadStatus("Still processing...");
          }
        } catch {
          clearInterval(poll);
          setUploadStatus("Status check failed.");
        }
      }, 2000);
    } catch {
      setUploadStatus("Upload failed.");
      setIsUploading(false);
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // -- Session helpers --------------------------------------------------
  const handleNewChat = () => {
    setMessages([]);
    setActiveSessionId(null);
    setAskError(null);
  };

  const handleSelectSession = async (session: QASession) => {
    setActiveSessionId(session.id);
    setMessages([]);
    try {
      const { data } = await apiClient.get("/qa/sessions/" + session.id);
      const loaded: ChatMessage[] = (data.messages ?? []).map(
        (m: { role: string; content: string; sources?: SourceCitation[]; confidence?: string }) => ({
          role: m.role === "user" ? "user" : "assistant",
          content: m.content,
          citations: m.role !== "user" ? (m.sources ?? []) : undefined,
          confidence: m.confidence,
        })
      );
      setMessages(loaded);
    } catch {
      // session history unavailable, start fresh in this session
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem("documind_access_token");
    window.location.replace("/login");
  };

  // -- Loading / unauthed states ----------------------------------------
  if (loading) {
    return (
      <div
        className="flex min-h-screen items-center justify-center"
        style={{ background: "var(--background)" }}
      >
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
      </div>
    );
  }

  if (!user) return null;

  // -- Render -----------------------------------------------------------
  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ background: "var(--background)", color: "var(--foreground)" }}
    >
      {/* -- Sidebar -- */}
      <aside
        className="flex w-60 flex-shrink-0 flex-col"
        style={{
          borderRight: "1px solid var(--border-subtle)",
          background: "var(--accent-soft)",
        }}
      >
        {/* Logo + New chat */}
        <div className="flex items-center justify-between px-4 py-4">
          <span className="text-sm font-semibold tracking-tight">DocuMind</span>
          <Button variant="ghost" size="sm" onClick={handleNewChat}>
            + New
          </Button>
        </div>

        {/* Upload */}
        <div className="px-3 pb-3">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            className="hidden"
            onChange={handleUpload}
          />
          <Button
            variant="outline"
            size="sm"
            className="w-full text-xs"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            {isUploading ? "Uploading..." : "Upload document"}
          </Button>
          {uploadStatus && (
            <p
              className="mt-1 truncate text-xs"
              style={{ color: "var(--foreground)", opacity: 0.6 }}
              title={uploadStatus}
            >
              {uploadStatus}
            </p>
          )}
        </div>

        {/* Scrollable content */}
        <div className="flex-1 space-y-4 overflow-y-auto px-2 pb-4">
          {/* Collections */}
          {collections.length > 0 && (
            <section>
              <p
                className="px-2 py-1 text-xs font-medium uppercase tracking-wide"
                style={{ color: "var(--foreground)", opacity: 0.45 }}
              >
                Collections
              </p>
              <ul className="space-y-0.5">
                <li>
                  <button
                    onClick={() => setSelectedCollectionId(null)}
                    className={cn(
                      "w-full rounded px-2 py-1.5 text-left text-xs transition-colors",
                      selectedCollectionId === null
                        ? "bg-indigo-600/20 font-medium text-indigo-400"
                        : "hover:bg-white/5"
                    )}
                    style={
                      selectedCollectionId !== null
                        ? { color: "var(--foreground)", opacity: 0.7 }
                        : {}
                    }
                  >
                    All documents
                  </button>
                </li>
                {(collections as Collection[]).map((c) => (
                  <li key={c.id}>
                    <button
                      onClick={() =>
                        setSelectedCollectionId(
                          selectedCollectionId === c.id ? null : c.id
                        )
                      }
                      className={cn(
                        "w-full truncate rounded px-2 py-1.5 text-left text-xs transition-colors",
                        selectedCollectionId === c.id
                          ? "bg-indigo-600/20 font-medium text-indigo-400"
                          : "hover:bg-white/5"
                      )}
                      style={
                        selectedCollectionId !== c.id
                          ? { color: "var(--foreground)", opacity: 0.7 }
                          : {}
                      }
                    >
                      {c.name}
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Recent sessions */}
          {(sessions as QASession[]).length > 0 && (
            <section>
              <p
                className="px-2 py-1 text-xs font-medium uppercase tracking-wide"
                style={{ color: "var(--foreground)", opacity: 0.45 }}
              >
                Recent chats
              </p>
              <ul className="space-y-0.5">
                {(sessions as QASession[]).map((s) => (
                  <li key={s.id}>
                    <button
                      onClick={() => handleSelectSession(s)}
                      className={cn(
                        "w-full truncate rounded px-2 py-1.5 text-left text-xs transition-colors",
                        activeSessionId === s.id
                          ? "bg-indigo-600/20 font-medium text-indigo-400"
                          : "hover:bg-white/5"
                      )}
                      style={
                        activeSessionId !== s.id
                          ? { color: "var(--foreground)", opacity: 0.7 }
                          : {}
                      }
                    >
                      {s.title ?? "Untitled session"}
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>

        {/* User footer */}
        <div
          className="px-4 py-3"
          style={{ borderTop: "1px solid var(--border-subtle)" }}
        >
          <p
            className="truncate text-xs"
            style={{ color: "var(--foreground)", opacity: 0.5 }}
          >
            {user.email}
          </p>
          <button
            onClick={handleSignOut}
            className="mt-1 text-xs transition-opacity hover:opacity-70"
            style={{ color: "var(--foreground)", opacity: 0.4 }}
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* -- Main chat area -- */}
      <main className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header
          className="flex items-center px-6 py-3"
          style={{ borderBottom: "1px solid var(--border-subtle)" }}
        >
          <div>
            <h1 className="text-sm font-medium">
              {activeSessionId ? "Continuing session" : "New chat"}
            </h1>
            {selectedCollectionId && (
              <p
                className="text-xs"
                style={{ color: "var(--foreground)", opacity: 0.5 }}
              >
                {"Collection: " +
                  ((collections as Collection[]).find(
                    (c) => c.id === selectedCollectionId
                  )?.name ?? "")}
              </p>
            )}
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 space-y-6 overflow-y-auto px-6 py-4">
          {messages.length === 0 && !isAsking && (
            <div className="flex h-full flex-col items-center justify-center gap-2 text-center">
              <p
                className="text-lg font-medium"
                style={{ color: "var(--foreground)", opacity: 0.7 }}
              >
                Ask anything about your documents
              </p>
              <p
                className="text-sm"
                style={{ color: "var(--foreground)", opacity: 0.4 }}
              >
                Upload a document from the sidebar, then ask a question below.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                "flex gap-3",
                msg.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              {msg.role === "assistant" && (
                <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-indigo-600 text-xs font-bold text-white">
                  D
                </div>
              )}

              <div
                className="max-w-2xl rounded-xl px-4 py-3 text-sm"
                style={
                  msg.role === "user"
                    ? { background: "#4f46e5", color: "#fff" }
                    : {
                        background: "var(--accent-soft)",
                        color: "var(--foreground)",
                        border: "1px solid var(--border-subtle)",
                      }
                }
              >
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                {msg.citations && msg.citations.length > 0 && (
                  <div
                    className="mt-3 space-y-2 pt-3"
                    style={{ borderTop: "1px solid rgba(255,255,255,0.12)" }}
                  >
                    <p className="text-xs font-medium" style={{ opacity: 0.65 }}>
                      Sources
                    </p>
                    {msg.citations.slice(0, 3).map((c, ci) => (
                      <div
                        key={ci}
                        className="rounded-lg px-3 py-2 text-xs"
                        style={{ background: "rgba(0,0,0,0.18)" }}
                      >
                        {c.title && (
                          <p className="mb-0.5 font-medium">
                            {c.title +
                              (c.page != null ? " p. " + String(c.page) : "") +
                              (c.section ? " - " + c.section : "")}
                          </p>
                        )}
                        <p className="line-clamp-2 leading-relaxed opacity-80">
                          {c.chunk_text}
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {msg.confidence && (
                  <p className="mt-2 text-xs" style={{ opacity: 0.45 }}>
                    {"Confidence: " + msg.confidence}
                  </p>
                )}
              </div>

              {msg.role === "user" && (
                <div
                  className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-xs font-bold"
                  style={{ background: "rgba(255,255,255,0.1)" }}
                >
                  {(user.email?.[0] ?? "U").toUpperCase()}
                </div>
              )}
            </div>
          ))}

          {/* Typing indicator */}
          {isAsking && (
            <div className="flex gap-3 justify-start">
              <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-indigo-600 text-xs font-bold text-white">
                D
              </div>
              <div
                className="rounded-xl px-4 py-3"
                style={{
                  background: "var(--accent-soft)",
                  border: "1px solid var(--border-subtle)",
                }}
              >
                <div className="flex items-center gap-1.5">
                  <span
                    className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce"
                    style={{ animationDelay: "0ms" }}
                  />
                  <span
                    className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce"
                    style={{ animationDelay: "150ms" }}
                  />
                  <span
                    className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce"
                    style={{ animationDelay: "300ms" }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Error */}
          {askError && (
            <div
              className="rounded-xl px-4 py-3 text-sm text-red-400"
              style={{
                background: "rgba(239,68,68,0.08)",
                border: "1px solid rgba(239,68,68,0.2)",
              }}
            >
              {askError}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div
          className="px-4 py-3"
          style={{ borderTop: "1px solid var(--border-subtle)" }}
        >
          <div
            className="flex items-end gap-2 rounded-xl px-3 py-2"
            style={{
              border: "1px solid var(--border-subtle)",
              background: "var(--accent-soft)",
            }}
          >
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your documents..."
              rows={1}
              className="flex-1 resize-none bg-transparent text-sm outline-none"
              style={{
                minHeight: "1.5rem",
                maxHeight: "8rem",
                color: "var(--foreground)",
              }}
              disabled={isAsking}
            />
            <Button
              onClick={handleAsk}
              disabled={!question.trim() || isAsking}
              size="sm"
              className="flex-shrink-0"
            >
              Send
            </Button>
          </div>
          <p
            className="mt-1.5 text-center text-xs"
            style={{ color: "var(--foreground)", opacity: 0.28 }}
          >
            Enter to send - Shift+Enter for newline
          </p>
        </div>
      </main>
    </div>
  );
}
