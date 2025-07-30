import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MasterFormat PDF to JSON Parser",
  description: "Upload PDF files and convert them to structured JSON format using AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="font-mono antialiased">
        {children}
      </body>
    </html>
  );
}
