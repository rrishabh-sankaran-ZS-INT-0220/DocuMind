"use client";

import { Mic } from "lucide-react";

export interface VoiceButtonProps {
  onVoice?: () => void;
  disabled?: boolean;
}

export function VoiceButton({ onVoice, disabled }: VoiceButtonProps) {
  return (
    <button
      type="button"
      aria-label="Voice input"
      onClick={onVoice}
      disabled={disabled}
      className="
        inline-flex
        h-11
        w-11
        items-center
        justify-center
        rounded-full
        border
        border-[#2B2B2B]
        bg-[#1A1A1A]
        text-[#F5F5F5]
        transition-colors
        hover:bg-[#232323]
        focus-visible:outline-none
        focus-visible:ring-2
        focus-visible:ring-[#2F80ED]/25
        disabled:cursor-not-allowed
        disabled:opacity-60
      "
    >
      <Mic aria-hidden="true" size={18} strokeWidth={2.2} />
    </button>
  );
}