"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { BrandAvatar } from "@/constants/BrandAvatar";
import FeatureCard from "@/components/landing/FeatureCard";
import Workflow from "@/components/landing/Workflow";
import TechStack from "@/components/landing/TechStack";
import UseCases from "@/components/landing/UseCases";
import SiteFooter from "@/components/landing/SiteFooter";

const features = [
  { title: "Document Understanding", description: "Upload PDFs, DOCX, Markdown and TXT files. Build an intelligent searchable knowledge base." },
  { title: "AI Question Answering", description: "Ask questions in natural language. Receive contextual answers with citations." },
  { title: "Document Comparison", description: "Compare multiple files. Detect similarities and differences." },
  { title: "Smart Summaries", description: "Generate concise summaries of lengthy documents." },
  { title: "Semantic Search", description: "Search by meaning instead of keywords using vector embeddings." },
  { title: "Collections", description: "Organize documents into independent workspaces." },
];

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--text)]">
      <header className="sticky top-0 z-40 w-full backdrop-blur-sm">
        <div className="mx-auto flex w-full max-w-[1400px] items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <div className="flex items-center gap-3">
            <BrandAvatar size={36} />
            <div>
              <p className="text-sm font-semibold">DocuMind</p>
              <p className="text-xs text-[var(--text-muted)]">AI Knowledge Workspace</p>
            </div>
          </div>

          <nav className="flex items-center gap-3">
            <a href="#" className="rounded-md px-3 py-2 text-sm text-[var(--text-muted)] hover:text-[var(--text)]">Documentation</a>
            <a href="https://github.com" target="_blank" rel="noreferrer" className="rounded-md px-3 py-2 text-sm text-[var(--text-muted)] hover:text-[var(--text)]">GitHub</a>
            <button onClick={() => router.push('/login')} className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm font-semibold text-[var(--text)] hover:border-[var(--accent)]">Sign In</button>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-[1400px] px-4 pb-16 sm:px-6">
        {/* HERO */}
        <section className="grid gap-8 py-12 lg:grid-cols-2 lg:items-center">
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.36 }}>
            <p className="inline-flex rounded-full border border-[var(--border)] bg-[var(--card)] px-3 py-1 text-xs uppercase tracking-[0.2em] text-[var(--text-muted)]">AI Knowledge Workspace</p>
            <h1 className="mt-6 text-4xl font-semibold leading-tight tracking-tight text-[var(--text)] sm:text-5xl">Build a smarter<br/>Document AI Workspace.</h1>
            <p className="mt-4 max-w-xl text-lg text-[var(--text-muted)]">Transform documents into an intelligent knowledge base. Ask natural language questions. Summarize long reports. Compare multiple documents. Retrieve citation-backed answers.</p>

            <div className="mt-6 flex gap-3">
              <Button variant="primary" size="lg" onClick={() => router.push('/login')}>Get Started</Button>
              <Button variant="secondary" size="lg" className="hover:bg-gray-800/40 transition-colors" onClick={() => router.push('/login')}>Sign In</Button>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.36, delay: 0.06 }} className="flex items-center justify-center">
            <div className="w-full max-w-md rounded-[var(--radius-xl)] border border-[var(--border)] bg-[var(--card)] p-6 shadow-subtle">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold text-[var(--text)]">Try DocuMind</p>
                  <p className="mt-2 text-sm text-[var(--text-muted)]">Sign in to upload documents and query your knowledge base.</p>
                </div>
                <div className="hidden h-16 w-28 rounded-md bg-[var(--surface)] p-2 text-xs text-[var(--text-muted)] sm:block">
                  Preview
                </div>
              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3">
                  <p className="text-xs font-semibold text-[var(--text)]">Instant Answers</p>
                  <p className="mt-1 text-xs text-[var(--text-muted)]">Get citation-backed responses.</p>
                </div>
                <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3">
                  <p className="text-xs font-semibold text-[var(--text)]">Secure</p>
                  <p className="mt-1 text-xs text-[var(--text-muted)]">Google OAuth & JWT</p>
                </div>
                <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3">
                  <p className="text-xs font-semibold text-[var(--text)]">Fast Search</p>
                  <p className="mt-1 text-xs text-[var(--text-muted)]">Semantic retrieval via embeddings.</p>
                </div>
                <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3">
                  <p className="text-xs font-semibold text-[var(--text)]">Collections</p>
                  <p className="mt-1 text-xs text-[var(--text-muted)]">Organize by workspace.</p>
                </div>
              </div>
            </div>
          </motion.div>
        </section>

        {/* FEATURES */}
        <section className="mt-8">
          <h3 className="text-lg font-semibold text-[var(--text)]">Features</h3>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => (
              <FeatureCard key={f.title} title={f.title} description={f.description} />
            ))}
          </div>
        </section>

        {/* WORKFLOW */}
        <section className="mt-10">
          <h3 className="text-lg font-semibold text-[var(--text)]">How it works</h3>
          <div className="mt-4">
            <Workflow />
          </div>
        </section>

        {/* WHY */}
        <section className="mt-10">
          <h3 className="text-lg font-semibold text-[var(--text)]">Why DocuMind</h3>
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {[
              'Retrieval-Augmented Generation (RAG)',
              'Citation-backed answers',
              'Fast semantic search',
              'Multi-document reasoning',
              'Google OAuth authentication',
              'Modern AI workspace',
            ].map((t) => (
              <div key={t} className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-3 text-sm text-[var(--text-muted)]">{t}</div>
            ))}
          </div>
        </section>

        {/* TECH STACK */}
        <section className="mt-10">
          <h3 className="text-lg font-semibold text-[var(--text)]">Tech Stack</h3>
          <div className="mt-4">
            <TechStack />
          </div>
        </section>

        {/* USE CASES */}
        <section className="mt-10">
          <h3 className="text-lg font-semibold text-[var(--text)]">Use Cases</h3>
          <div className="mt-4">
            <UseCases />
          </div>
        </section>

        {/* CTA */}
        <section className="mt-12 text-center">
          <div className="mx-auto max-w-2xl rounded-[var(--radius-xl)] border border-[var(--border)] bg-[var(--card)] p-8">
            <h3 className="text-2xl font-semibold text-[var(--text)]">Ready to build your AI workspace?</h3>
            <p className="mt-2 text-sm text-[var(--text-muted)]">Start with your documents and get instant, cited answers.</p>
            <div className="mt-6 flex justify-center gap-3">
              <Button variant="primary" size="lg" onClick={() => router.push('/login')}>Get Started</Button>
              <Button variant="secondary" size="lg" className="hover:bg-gray-800/40 transition-colors" onClick={() => router.push('/login')}>Sign In</Button>
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}