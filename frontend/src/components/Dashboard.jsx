"use client";

import { Suspense } from "react";
import { PiGrid } from "./PiGrid";
import { DashboardHeader } from "./DashboardHeader";
import { useState, useEffect } from "react";

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
    <div className="">
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
        <div className="height-100vh w-[3/4] items-center justify-center py-[10rem] text-center ">
          <h1 className="font-extrabold text-[4rem]">
            How Do I know You're Eligible to Enter?
          </h1>
          <input
            type="password"
            onChange={handleTextEntered}
            autoFocus
            placeholder="Tell me a secret"
            className="bg-blue-100 text-center placeholder-shown:text-center w-[75%] h-12 text-3xl max-lg:text-2xl max-lg:w-[90%] mt-[5%] rounded-lg focus:outline-none"
          ></input>
        </div>
      )}
    </div>
  );
}
