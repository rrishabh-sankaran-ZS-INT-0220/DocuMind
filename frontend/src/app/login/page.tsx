"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { apiClient } from "../../lib/api";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/auth-context";
import { FcGoogle } from "react-icons/fc";

export default function LoginPage() {
  const router = useRouter();
  const { setAccessToken, setRefreshToken } = useAuth();

  const handleGoogleLogin = async () => {
    try {
      const res = await apiClient.post("/auth/google/login", {
        provider: "google",
      });
      const url = res.data.authorization_url;
      window.location.href = url;
    } catch (err) {
      console.error("Google login failed", err);
      alert("Unable to start Google login. Please try again.");
    }
  };

  const handleDevLogin = async () => {
    try {
      const res = await apiClient.post("/auth/dev-login");

      const { access_token, refresh_token } = res.data;

      setAccessToken(access_token);
      setRefreshToken(refresh_token);
      router.replace("/dashboard");
    } catch (err) {
      console.error("Dev login failed", err);
      alert("Unable to sign in as developer. Check backend ENABLE_DEV_LOGIN.");
    }
  };

  const enableDevLogin =
    typeof process.env.NEXT_PUBLIC_ENABLE_DEV_LOGIN !== "undefined" &&
    process.env.NEXT_PUBLIC_ENABLE_DEV_LOGIN === "true";

  const GoogleIcon = () => (
    <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white shadow-sm">
      <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden="true" fill="none">
        <path d="M21.35 11.1h-9.36v2.8h5.38c-.24 1.55-1.51 4.55-5.38 4.55-3.24 0-5.88-2.68-5.88-6s2.64-6 5.88-6c1.84 0 3.06.78 3.76 1.45l2.56-2.48C17.54 2.54 15.1 1 12 1 6.48 1 2 5.48 2 11s4.48 10 10 10c5.78 0 9.55-4.04 9.55-9.73 0-.66-.08-1.3-.2-1.47z" fill="#4285F4" />
        <path d="M3.6 7.9l3.05 2.24C7.18 8.06 9.43 6.5 12 6.5c1.84 0 3.06.78 3.76 1.45l2.56-2.48C17.54 2.54 15.1 1 12 1 7.58 1 3.97 3.57 3.6 7.9z" fill="#34A853" />
        <path d="M12 23c3.1 0 5.54-1.06 7.52-2.9l-3.47-2.74C14.95 17.6 13.57 18 12 18c-3.87 0-5.14-3-5.38-4.55L3.6 14.1C4.04 17.9 7.58 23 12 23z" fill="#FBBC05" />
        <path d="M21.35 11.1h-9.36v2.8h5.38c-.24 1.55-1.51 4.55-5.38 4.55-3.24 0-5.88-2.68-5.88-6 0-.62.09-1.22.25-1.8L3.6 7.9C3.27 8.96 3 10.19 3 11.5c0 1.83.6 3.51 1.6 4.85L7.2 14.1c-.08-.36-.12-.73-.12-1.1 0-.37.04-.74.12-1.1L3.6 7.9C3.27 8.96 3 10.19 3 11.5c0 1.83.6 3.51 1.6 4.85L7.2 14.1c-.08-.36-.12-.73-.12-1.1 0-.37.04-.74.12-1.1L3.6 7.9z" fill="#EA4335" />
      </svg>
    </span>
  );

  return (
    <div className="min-h-screen w-screen bg-[var(--background)] text-[var(--text)] flex items-center justify-center">
      <motion.main
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.28, ease: "easeOut" }}
        className="w-full max-w-[520px] rounded-[var(--radius-xl)] border border-[var(--border)] bg-[var(--card)] p-10 shadow-subtle"
      >
        <div className="space-y-8 text-center">
          <div className="space-y-3">
            <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-white/5">
              <div className="h-2.5 w-2.5 rounded-full bg-[var(--accent)]" />
            </div>
            <div>
              <p className="text-xl font-semibold text-[var(--text)]">DocuMind</p>
              <p className="text-sm text-[var(--text-muted)]">AI Knowledge Workspace</p>
            </div>
          </div>

          <div className="space-y-3 text-center">
            <h1 className="text-3xl font-semibold text-[var(--text)]">Sign in to DocuMind</h1>
            <p className="text-sm leading-6 text-[var(--text-muted)]">
              Continue with your Google account to access your documents and conversations.
            </p>
          </div>

          <div className="space-y-4">
            <Button
              variant="primary"
              size="lg"
              className="relative h-12 w-full rounded-xl bg-black text-white hover:bg-neutral-900"
              onClick={handleGoogleLogin}
              aria-label="Continue with Google"
            >
              <span className="relative flex w-full items-center justify-center">
                <span className="absolute left-4 flex items-center justify-center">
                  <FcGoogle size={24} />
                </span>

                <span className="font-medium">
                  Continue with Google
                </span>
              </span>
            </Button>

            {enableDevLogin && (
              <>
                <div className="flex items-center gap-3 text-xs uppercase tracking-[0.24em] text-[var(--text-muted)]">
                  <span className="h-px flex-1 bg-[var(--border)]" />
                  <span>OR</span>
                  <span className="h-px flex-1 bg-[var(--border)]" />
                </div>
                <Button
                  variant="secondary"
                  size="lg"
                  className="h-12 w-full rounded-xl border-[var(--border)] bg-[var(--card)] text-[var(--text)] hover:bg-[var(--surface)]"
                  onClick={handleDevLogin}
                  aria-label="Continue as Developer"
                >
                  Continue as Developer
                </Button>
              </>
            )}
          </div>

          <p className="text-center text-xs leading-5 text-[var(--text-muted)]">
            By signing in you agree to the <a href="#" className="text-[var(--text)] underline decoration-[var(--border)] decoration-1 underline-offset-2 hover:text-white">Terms of Service</a> and <a href="#" className="text-[var(--text)] underline decoration-[var(--border)] decoration-1 underline-offset-2 hover:text-white">Privacy Policy</a>.
          </p>
        </div>
      </motion.main>
    </div>
  );
}