import type { Metadata, Viewport } from "next";
import Script from "next/script";
// @ts-expect-error Next.js processes global CSS imports at build time.
import "./globals.css";

export const metadata: Metadata = {
  title: "QADAM - Kasb yonaltiruvchi tahlil",
  description: "Sizga mos kasb va sohani toping",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: "#0a0a0f",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uz">
      <head>
        <Script
          src="https://telegram.org/js/telegram-web-app.js"
          strategy="beforeInteractive"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
