"use client";

import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api";

export default function LoginPage() {
  const handleGoogleLogin = async () => {
    const res = await apiClient.post("/auth/google/login", {
      provider: "google",
    });
    const url = res.data.authorization_url;
    window.location.href = url;
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-md rounded-xl border border-border-subtle bg-accent-soft/40 p-6 shadow-lg">
        <h1 className="mb-2 text-xl font-semibold">Sign in to DocuMind</h1>
        <p className="mb-6 text-sm text-foreground/70">
          Use your Google account to continue.
        </p>
        <Button
          variant="default"
          size="lg"
          className="w-full"
          onClick={handleGoogleLogin}
        >
          Continue with Google
        </Button>
      </div>
    </div>
  );
}
