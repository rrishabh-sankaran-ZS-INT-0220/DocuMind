// src/lib/api.ts
import axios from "axios";

export const apiClient = axios.create({
  // Adjust this baseURL to match your backend URL.
  // For local dev with backend on port 8000:
  // baseURL: "http://localhost:8000/api/v1",
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1",
  withCredentials: false,
  headers: {
    "Content-Type": "application/json",
  },
});