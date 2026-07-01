"use client";

export interface AttachmentChipProps {
  fileName: string;
  onRemove: () => void;
}

export function AttachmentChip({ fileName, onRemove }: AttachmentChipProps) {
  return (
    <div className="mt-1 flex items-center justify-between rounded-full bg-[#262626] px-3 py-1 text-xs text-[#ECECEC]">
      <span className="flex items-center gap-2">
        <span>📄</span>
        <span className="truncate max-w-[260px]">{fileName}</span>
      </span>
      <button
        type="button"
        className="text-[#A1A1AA] hover:text-[#ECECEC] text-[11px]"
        onClick={onRemove}
      >
        Remove
      </button>
    </div>
  );
}