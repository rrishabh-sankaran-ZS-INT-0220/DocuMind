import "./globals.css";
import { Inter } from "next/font/google";
import type { Metadata } from "next";
import { ThemeProvider } from "@/components/theme-provider";
import { Providers } from "@/components/providers";

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