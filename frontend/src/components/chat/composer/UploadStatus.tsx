"use client";

import { Loader2, CheckCircle2 } from "lucide-react";

interface UploadStatusProps {
  uploading?: boolean;
  status?: string;
}

export function UploadStatus({
  uploading = false,
  status,
}: UploadStatusProps) {
  if (!status) return null;

  return (
    <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
      {uploading ? (
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
      ) : (
        <CheckCircle2 className="h-3.5 w-3.5 text-[var(--accent)]" />
      )}

      <span>{status}</span>
    </div>
  );
}