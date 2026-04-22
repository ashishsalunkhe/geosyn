import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "GeoSyn | Geopolitical Intelligence Platform",
  description: "Aggregate global news, cluster events, and track narrative shifts with market impact analysis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full overflow-x-hidden">
      <body className="min-h-full overflow-x-hidden bg-background antialiased">
        {children}
      </body>
    </html>
  );
}
