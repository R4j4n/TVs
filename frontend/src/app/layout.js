// app/layout.js

import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Aerosports",
  description: "Control multiple Raspberry Pi video players",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${inter.className} bg-gradient-to-b from-blue-100 to-pink-100 bg-fixed `}
      >
        {children}
      </body>
    </html>
  );
}
