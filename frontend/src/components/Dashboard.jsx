// components/Dashboard.jsx

"use client";

import { Suspense, useState, useEffect } from "react";
import { PiGrid } from "./PiGrid";
import { DashboardHeader } from "./DashboardHeader";
import { Orbitron } from "next/font/google";

const orbitron = Orbitron({
  subsets: ["latin"],
  weight: ["400", "700"],
});

export default function Dashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleTextEntered = (e) => {
    if (e.target.value === process.env.NEXT_PUBLIC_PROJECT_ID) {
      setIsAuthenticated(true);
      sessionStorage.setItem("isAuthenticated", "Yes");
    }
  };

  useEffect(() => {
    if (sessionStorage.getItem("isAuthenticated") === "Yes") {
      setIsAuthenticated(true);
    }
  }, []);

  return (
    <div className="w-full h-[100vh] text-center ">
      {isAuthenticated == true ? (
        <div className="min-h-screen p-8">
          <div className="max-w-7xl mx-auto space-y-8">
            <DashboardHeader />
            <Suspense fallback={<div>Loading...</div>}>
              <PiGrid />
            </Suspense>
          </div>
        </div>
      ) : (
        <div className="h-full w-full bg-banner bg-cover bg-center items-center justify-center flex ">
          <div className="h-fit w-[75%] backdrop-blur-lg bg-slate-100/10 brightness-75 rounded-xl drop-shadow-2xl items-center justify-center py-[10rem] text-center text-white ">
            <h1
              className={`font-extrabold text-[2.5rem] pb-10 ${orbitron.className}`}
            >
              Welcome to Integrated Media Player Interface
            </h1>
            <h3 className="text-[1.8rem] pb-0 mb-0">
              Please Enter your passcode . . .
            </h3>
            <input
              type="password"
              onChange={handleTextEntered}
              autoFocus
              placeholder="Passcode . . ."
              className="bg-blue-100 text-blue-800 text-center placeholder-shown:text-center w-[75%] md:w-[50%] h-12 text-3xl max-lg:text-2xl max-lg:w-[90%] mt-[5%] rounded-lg focus:outline-none "
            ></input>
          </div>
        </div>
      )}
    </div>
  );
}
