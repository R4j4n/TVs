// components/DashboardHeader.jsx

"use client";

import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { Montserrat } from "next/font/google";

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["400", "700"],
});

export function DashboardHeader() {
  const router = useRouter();
  return (
    <div
      className={`flex items-center justify-between pb-10 ${montserrat.className}`}
    >
      <h1 className="text-4xl font-bold">Extensive Multimedia Control Panel</h1>
      <Button onClick={() => router.refresh()}>
        <RefreshCw className="h-4 w-4 mr-2" />
        Refresh All
      </Button>
    </div>
  );
}
