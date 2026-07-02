"use client";

import { KeyboardEvent, useRef } from "react";
import { cn } from "@/lib/utils";
import { useAutoResizeTextarea } from "@/hooks/useAutoResizeTextarea";

export interface PromptTextareaProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
}

export function PromptTextarea({
  value,
  onChange,
  onSend,
  disabled,
}: PromptTextareaProps) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useAutoResizeTextarea(textareaRef, value, { maxHeight: 240 });

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter sends, Shift+Enter inserts newline
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSend();
    }
  };

  return (
    <textarea
      ref={textareaRef}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      onKeyDown={handleKeyDown}
      placeholder="Message DocuMind..."
      className={cn(
        "w-full bg-transparent text-base leading-6 text-[#ECECEC]",
        "placeholder:text-[#A1A1AA]",
        "focus-visible:outline-none",
        "resize-none overflow-hidden",
        "py-2.5",
        "transition-[height] duration-150 ease-out"
      )}
      rows={1}
      disabled={disabled}
    />
  );
}