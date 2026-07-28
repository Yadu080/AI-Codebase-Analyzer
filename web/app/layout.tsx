import type { Metadata } from "next";
import { Sora, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const sora = Sora({
  subsets: ["latin"],
  variable: "--font-sora",
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-plex",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AI Codebase Analyzer",
  description:
    "Clone any GitHub repository, index it with semantic search, and ask grounded questions about the code.",
  metadataBase: new URL("https://ai-codebase-analyzer.vercel.app"),
  openGraph: {
    title: "AI Codebase Analyzer",
    description:
      "RAG-powered code exploration — FAISS, SentenceTransformers, Groq.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${sora.variable} ${plexMono.variable}`}>
      <body
        style={
          {
            ["--font-sans" as string]: "var(--font-sora), Sora, sans-serif",
            ["--font-mono" as string]:
              "var(--font-plex), 'IBM Plex Mono', monospace",
          } as React.CSSProperties
        }
      >
        {children}
      </body>
    </html>
  );
}
