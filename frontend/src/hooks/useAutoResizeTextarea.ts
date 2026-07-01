"use client";

import { MutableRefObject, useLayoutEffect } from "react";

interface UseAutoResizeTextareaOptions {
  maxHeight?: number;
}

/**
 * Auto-resizes a textarea based on its content height.
 * Keeps the behavior identical to the previous inline logic.
 */
export function useAutoResizeTextarea(
  textareaRef: MutableRefObject<HTMLTextAreaElement | null>,
  value: string,
  options: UseAutoResizeTextareaOptions = {}
) {
  const { maxHeight = 240 } = options;

  useLayoutEffect(() => {
    console.log("Hook running", textareaRef.current, value);

    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = "auto";

    const scrollHeight = textarea.scrollHeight;
    const newHeight = Math.min(scrollHeight, maxHeight);

    textarea.style.height = `${newHeight}px`;
    textarea.style.overflowY = scrollHeight > maxHeight ? "auto" : "hidden";
  }, [textareaRef, value, maxHeight]);
}