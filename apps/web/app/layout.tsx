import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Qteria - AI Document Pre-Assessment Platform",
  description: "Transform manual compliance checks into AI-powered assessments with evidence-based results in <10 minutes.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
