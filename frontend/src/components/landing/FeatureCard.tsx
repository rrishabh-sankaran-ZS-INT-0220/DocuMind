"use client";

import React from "react";
import { motion } from "framer-motion";

type Props = {
  title: string;
  description: string;
};

export default function FeatureCard({ title, description }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28 }}
      className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5"
    >
      <p className="text-sm font-semibold text-[var(--text)]">{title}</p>
      <p className="mt-2 text-sm text-[var(--text-muted)]">{description}</p>
    </motion.div>
  );
}
