"use client";

import { ChangeEvent, useRef } from "react";
import { IconButton } from "@/components/ui/icon-button";

export interface UploadButtonProps {
  onUpload: (file: File) => void;
  disabled?: boolean;
}

export function UploadButton({ onUpload, disabled }: UploadButtonProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    onUpload(file);
  };

  return (
    <>
      <IconButton
        aria-label="Attach document"
        onClick={handleAttachClick}
        disabled={disabled}
        className="text-[#A1A1AA] hover:text-[#ECECEC] hover:bg-[#3A3A3A] transition-[border-color,box-shadow,color,background-color] duration-150"
      >
        📎
      </IconButton>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt,.md"
        className="hidden"
        onChange={handleFileChange}
      />
    </>
  );
}