"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "@/context/auth-context";

export default function AuthCallbackPage() {
  const params = useSearchParams();
  const router = useRouter();
  const { setAccessToken, setRefreshToken } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");

    if (accessToken) {
      try {
        setAccessToken(accessToken);
        if (refreshToken) {
          setRefreshToken(refreshToken);
        }
        // After successful login, go to dashboard
        router.replace("/dashboard");
      } catch (e) {
        console.error("Error setting tokens from callback", e);
        setError("Failed to complete sign-in. Please try again.");
        router.replace("/login");
      }
    } else {
      setError("Missing access token. Please sign in again.");
      router.replace("/login");
    }
  }, [params, router, setAccessToken, setRefreshToken]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--background)] px-4">
      <div className="card px-4 py-3">
        {error ? (
          <p className="text-sm text-[var(--danger)]">{error}</p>
        ) : (
          <p className="text-sm text-[var(--text-muted)]">
            Completing sign-in…
          </p>
        )}
      </div>
    </div>
  );
}