import type { Metadata } from "next";
import "./globals.css";
import Providers from "@/components/Providers";

export const metadata: Metadata = {
  title: "가계부 분석기 - Analyzer",
  description: "개인 가계부 분석 서비스",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" className="light">
      <body className="bg-surface text-on-surface min-h-screen antialiased font-body">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
