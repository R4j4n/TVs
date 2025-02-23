// components/DashboardHeader.jsx

"use client";

import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { Montserrat } from "next/font/google";
import Image from "next/image";

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["400", "700"],
});

export function DashboardHeader() {
  const router = useRouter();
  return (
    <div
      className={`flex items-center justify-between pb-4 ${montserrat.className}`}
    >
      <div className="flex w-fit">
      <Image src="/logo.png" height={60} width={60} className="inline" alt="Logo" />
      <h1 className="text-3xl font-bold pl-4">AV Control Panel</h1>
      </div>
      <Button onClick={() => router.refresh()}>
        <RefreshCw className="h-3 w-4 mr-2 justify-end" />
        Refresh All
      </Button>
    </div>
  );
}
