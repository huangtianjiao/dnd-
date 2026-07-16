import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "AI DM — D&D 5E 跑团", description: "硬性判定链 AI DM" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh">
      <body>{children}</body>
    </html>
  );
}
