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
    // Update local attachment state and delegate upload
    setAttachment({ fileName: file.name });
    onUpload(file);
  };

  const handleRemoveAttachment = () => {
    setAttachment({ fileName: null });
  };

  return (
    <div className="flex flex-col gap-2">
      {/* Floating composer card */}
      <div
        className={cn(
          // Centered, responsive floating width
          "mx-auto w-full max-w-[880px] px-3 sm:px-4 md:px-6",
          // Rounded container with subtle border and background
          "rounded-[30px] border border-[#3A3A3A]/60 bg-[#1C1C1C]",
          // Soft, non-modal elevation
          "shadow-[0_10px_30px_rgba(0,0,0,0.35)]",
          // Smooth visual transitions for border/shadow (focus state)
          // "transition-[border-color,box-shadow] duration-150 ease-out",
          // Comfortable vertical padding
          "flex flex-col pt-4 pb-4 sm:pt-5 sm:pb-5"
        )}
      >
        {/* Content area: textarea + attached file chip */}
        <div className="flex flex-col flex-1 gap-3 px-1 sm:px-2">
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
        </div>

        {/* Toolbar row, visually attached via whitespace (no divider) */}
        <div className="mt-3">
          <ComposerToolbar
            onUpload={handleUpload}
            isUploading={isUploading}
            onSend={handleSend}
            disabledSend={disabledSend}
          />
        </div>
      </div>

      {/* Status / hints row aligned with composer */}
      <div className="mx-auto flex w-full max-w-[880px] items-center justify-between px-3 sm:px-4 md:px-6 text-xs text-[#A1A1AA]">
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