import type { Metadata, Viewport } from "next";
import { TmaProvider } from "@/components/TmaProvider";
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
      <body>
        <TmaProvider>{children}</TmaProvider>
      </body>
    </html>
  );
}
