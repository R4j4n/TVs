// app/layout.js

import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Aero Media",
  description: "Control multiple Raspberry Pi video players",
};

{/* TODO: alternative background color to-[#1069ac]/50 */}
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${inter.className} bg-gradient-to-b from-slate-400/40 to-[#520300]/40   bg-fixed `}
      >
        {children}
      </body>
    </html>
  );
}
