"use client";

import { Button } from "@/components/ui/button";

export interface SendButtonProps {
  onSend: () => void;
  disabled?: boolean;
}

export function SendButton({ onSend, disabled }: SendButtonProps) {
  return (
    <Button
      variant="primary"
      size="md"
      onClick={onSend}
      disabled={disabled}
      className="min-w-[64px] justify-center"
    >
      Send
    </Button>
  );
}