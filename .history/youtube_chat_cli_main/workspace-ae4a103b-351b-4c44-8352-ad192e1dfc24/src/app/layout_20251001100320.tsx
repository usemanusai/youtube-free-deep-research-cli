import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import { Providers } from "./providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "JAEGIS NexusSync - Adaptive RAG Service Dashboard",
  description: "RAG-powered podcast generation platform with adaptive query routing, hallucination detection, and multi-source content processing.",
  keywords: ["JAEGIS", "NexusSync", "RAG", "LangGraph", "Next.js", "TypeScript", "Podcast Generation", "AI"],
  authors: [{ name: "JAEGIS Team" }],
  openGraph: {
    title: "JAEGIS NexusSync Dashboard",
    description: "Adaptive RAG Service with intelligent content processing",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "JAEGIS NexusSync Dashboard",
    description: "Adaptive RAG Service with intelligent content processing",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
