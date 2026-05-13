import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "M365 Enterprise Control Center",
  description:
    "Internal Microsoft 365 reporting, auditing, monitoring and security operations.",
  robots: { index: false, follow: false },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
