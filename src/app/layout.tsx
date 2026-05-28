import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "PromptPilot AI — Save 40% on AI API Costs. Automatically.",
  description:
    "PromptPilot intelligently compresses your LLM prompts for ChatGPT, Claude, and Gemini — reducing token usage by 30–50% without losing output quality. Save money. Work smarter.",
  keywords: [
    "AI token optimization",
    "prompt compression",
    "ChatGPT cost reduction",
    "Claude API optimization",
    "LLM token saving",
    "prompt engineering",
    "AI API costs",
    "token counter",
  ],
  authors: [{ name: "PromptPilot AI" }],
  openGraph: {
    title: "PromptPilot AI — Save 40% on AI API Costs",
    description:
      "Intelligently compress LLM prompts. Cut token usage 30–50%. No quality loss.",
    type: "website",
    url: "https://promptpilot.ai",
  },
  twitter: {
    card: "summary_large_image",
    title: "PromptPilot AI — Save 40% on AI API Costs",
    description: "Compress your AI prompts. Save real money. Works with GPT, Claude, Gemini.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased">{children}</body>
    </html>
  );
}
