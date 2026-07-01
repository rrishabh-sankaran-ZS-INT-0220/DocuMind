"use client";

import { UploadButton } from "./UploadButton";
import { SendButton } from "./SendButton";

export interface ComposerToolbarProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
  onSend: () => void;
  disabledSend: boolean;
}

export function ComposerToolbar({
  onUpload,
  isUploading,
  onSend,
  disabledSend,
}: ComposerToolbarProps) {
  return (
    <div className="flex items-center justify-between gap-3">
      <div className="flex items-center gap-2.5">
        {/* Upload button */}
        <UploadButton onUpload={onUpload} disabled={isUploading} />

        {/* Collection selector placeholder */}
        <button
          type="button"
          className="hidden text-xs text-[#A1A1AA] hover:text-[#ECECEC]"
        >
          {/* Future: collection selector */}
        </button>
      </div>

      {/* Send button anchored bottom-right visually */}
      <SendButton onSend={onSend} disabled={disabledSend} />
    </div>
  );
}