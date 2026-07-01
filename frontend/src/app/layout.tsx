import "./globals.css";
import { Inter } from "next/font/google";
import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ThemeProvider } from "@/components/theme-provider";
import { Providers } from "@/components/providers";
import { LOGO } from "@/config/logo";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "DocuMind",
  description: "AI workspace for document intelligence",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className + " min-h-screen bg-[var(--background)] text-[var(--text)]"}>
        <ThemeProvider>
          <Providers>
            <div className="flex min-h-screen flex-col">
              {/* Global Header */}
              <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--surface)]">
                <div className="flex items-center justify-between px-4 py-3 sm:px-6">
                  <Link href="/" className="flex items-center gap-2">
                    <Image
                      src={LOGO.icon}
                      alt={LOGO.alt}
                      width={LOGO.width}
                      height={LOGO.height}
                    />
                    <div className="flex flex-col">
                      <span className="text-sm font-semibold tracking-tight text-[var(--text)]">
                        DocuMind
                      </span>
                      <span className="text-xs text-[var(--text-muted)]">
                        AI workspace for document intelligence
                      </span>
                    </div>
                  </Link>
                  {/* Right side (search/theme/profile) can remain page-level for now */}
                </div>
              </header>

              {/* Main content area (Sidebar + Workspace) */}
              <main className="flex flex-1 bg-[var(--background)]">
                {children}
              </main>
            </div>
          </Providers>
        </ThemeProvider>
      </body>
    </html>
  );
}