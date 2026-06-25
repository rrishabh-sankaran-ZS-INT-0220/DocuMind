"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/context/auth-context";

export default function AuthCallbackPage() {
  const params = useSearchParams();
  const router = useRouter();
  const { setAccessToken } = useAuth();

  useEffect(() => {
    const accessToken = params.get("access_token");
    if (accessToken) {
      setAccessToken(accessToken);
      router.replace("/ask");
    } else {
      router.replace("/login");
    }
  }, [params, router, setAccessToken]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <p className="text-sm text-foreground/80">Completing sign-in…</p>
    </div>
  );
}
