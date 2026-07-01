// src/lib/hooks.ts
"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";

export type Collection = {
  id: string;
  name: string;
  // add any other fields your backend returns if needed
};

export type QASession = {
  id: string;
  title?: string | null;
  name?: string | null;
  created_at?: string;
  // add any other fields your backend returns if needed
};

export function useCollections() {
  return useQuery<Collection[]>({
    queryKey: ["collections"],
    queryFn: async () => {
      const { data } = await apiClient.get("/collections");
      // Expecting the backend to return an array of collections
      return data;
    },
    staleTime: 30_000,
  });
}

export function useQASessions() {
  return useQuery<QASession[]>({
    queryKey: ["qa-sessions"],
    queryFn: async () => {
      const { data } = await apiClient.get("/qa/sessions");
      // Expecting backend to return a list of sessions
      return data;
    },
    staleTime: 30_000,
  });
}