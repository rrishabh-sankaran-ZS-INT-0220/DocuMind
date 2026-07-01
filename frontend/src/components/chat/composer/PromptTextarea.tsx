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
        "w-full bg-transparent text-[17px] leading-relaxed text-[#ECECEC]",
        "placeholder:text-[#A1A1AA]",
        "focus-visible:outline-none",
        "resize-none overflow-hidden",
        // Vertical padding to visually center placeholder and text
        "py-3 sm:py-3.5",
        // Smooth but subtle height changes
        "transition-[height] duration-150 ease-out"
      )}
      rows={1}
      disabled={disabled}
    />
  );
}