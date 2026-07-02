"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { AttachmentChip } from "./AttachmentChip";
import { PromptTextarea } from "./PromptTextarea";
import { ComposerToolbar } from "./ComposerToolbar";
import type { ChatComposerProps, AttachmentState } from "./types";

export function ChatComposer({
  question,
  setQuestion,
  isAsking,
  onAsk,
  onUpload,
  isUploading,
  uploadStatus,
}: ChatComposerProps) {
  const [attachment, setAttachment] = useState<AttachmentState>({
    fileName: null,
  });

  const disabledSend = !question.trim() || isAsking;

  const handleSend = () => {
    onAsk();
  };

  const handleUpload = (file: File) => {
    setAttachment({ fileName: file.name });
    onUpload(file);
  };

  const handleVoice = () => {
    // Placeholder for future voice capture / speech-to-text integration.
  };

  const handleRemoveAttachment = () => {
    setAttachment({ fileName: null });
  };

  return (
    <div className="flex flex-col gap-3">
      <div
        className={cn(
          "mx-auto w-full max-w-[880px]",
          "rounded-[30px]",
          "border border-[#3A3A3A]/60",
          "bg-[#1C1C1C]",
          "shadow-[0_8px_24px_rgba(0,0,0,0.25)]",
          "overflow-hidden"
        )}
      >
        <div className="flex flex-col gap-3 px-5 py-4">
          <PromptTextarea
            value={question}
            onChange={setQuestion}
            onSend={handleSend}
            disabled={isAsking}
          />

          {attachment.fileName && (
            <AttachmentChip
              fileName={attachment.fileName}
              onRemove={handleRemoveAttachment}
            />
          )}

          <ComposerToolbar
            onUpload={handleUpload}
            isUploading={isUploading}
            onVoice={handleVoice}
            onSend={handleSend}
            disabledSend={disabledSend}
          />
        </div>
      </div>

      <div className="mx-auto flex w-full max-w-[880px] items-center justify-between px-2 text-xs text-[#A1A1AA]">
        <span>Enter to send · Shift+Enter for newline</span>

        {uploadStatus && (
          <span>
            {isUploading ? "Uploading: " : ""}
            {uploadStatus}
          </span>
        )}
      </div>
    </div>
  );
}