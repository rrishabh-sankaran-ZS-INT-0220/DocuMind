export interface ChatComposerProps {
  question: string;
  setQuestion: (value: string) => void;
  isAsking: boolean;
  onAsk: () => void;
  onUpload: (file: File) => void;
  isUploading: boolean;
  uploadStatus?: string;
}

export interface AttachmentState {
  fileName: string | null;
}