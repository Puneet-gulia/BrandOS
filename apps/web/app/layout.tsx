import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "BrandOS — Your AI Creative Team",
  description: "AI-powered marketing campaign generator",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <header className="border-b border-border bg-background px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-foreground">BrandOS</h1>
            <span className="text-sm text-muted-foreground hidden sm:inline-block">Your AI Creative Team</span>
          </div>
        </header>
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}\n