// components/Dashboard.jsx
"use client";

import { Suspense, useState, useEffect } from "react";
import { PiGrid } from "./PiGrid";
import { DashboardHeader } from "./DashboardHeader";
import { Montserrat } from "next/font/google";
import { auth_login, fetchPis } from "@/lib/api";
import Image from "next/image";

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["400", "700"],
});

export default function Dashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [firstPi, setFirstPi] = useState(null);


  const get_all_pis_list = async (check_index=0) => {
    const all_pis = await fetchPis(process.env.NEXT_PUBLIC_ACTIVE_SERVER_HOSTNAME);
      if ((all_pis.length) >0){
        setFirstPi(all_pis[check_index].host);
      }
  }


  useEffect(() => {
    try{
      get_all_pis_list()
      const token = sessionStorage.getItem("authToken");
      if (token) {
        setIsAuthenticated(true);
      }
    } catch(e){
      get_all_pis_list(check_index=-1)
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const login_response = await auth_login(firstPi, password); 
      // TODO: Mistake! This should be the PI host
      if (login_response.ok) {
        const data = await login_response.json();
        sessionStorage.setItem("authToken", data.token);
        setIsAuthenticated(true);
      } else {
        setError(data.message || "Login failed. Please try again.");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  return (
    <div className="w-full h-[100vh] text-center">
      {isAuthenticated ? (
        <div className="min-h-screen p-8">
          <div className="max-w-7xl mx-auto space-y-8">
            <DashboardHeader />
            <Suspense fallback={<div>Loading...</div>}>
              <PiGrid />
            </Suspense>
          </div>
        </div>
      ) : (
          <div className="h-full w-full bg-banner bg-cover bg-center items-center justify-start flex">
            {/*  TODO: change background blur from here */}
            <div className="m-0 p-0 w-full h-full bg-pink-800/10 flex justify-start items-center">
            
          <div className="h-fit w-[85%] md:w-[35%] md:ml-10 px-10 backdrop-blur-lg bg-slate-100/10 brightness-75 rounded-xl drop-shadow-2xl items-center justify-center py-[10rem] text-center text-white">
            <Image src="/logo.jpeg" width={150} height={100} className="m-auto pb-10 rounded-lg" alt="K1 Logo" />
                <h1
              className={`font-extrabold text-[2.2rem] pb-10 ${montserrat.className}`}
            >
              Welcome to Integrated Media Player Interface
            </h1>
            <h3 className="text-[1.2rem] pb-0 mb-0">
              Please Enter your passcode . . .
            </h3>
            <form onSubmit={handleLogin} className="mt-6 space-y-4">
              <input
                type="password"
                value={password}
                onChange={handlePasswordChange}
                autoFocus
                placeholder="Passcode . . ."
                className="bg-blue-100 text-blue-800 text-center placeholder-shown:text-center w-[75%] md:w-[50%] h-12 text-xl max-lg:text-2xl max-lg:w-[90%] rounded-lg focus:outline-none"
              />
              {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
              <button
                type="submit"
                disabled={isLoading}
                className="block mt-4 mx-auto px-10 py-3 bg-gradient-to-b  from-[#a60000] via-[#a60000] to-black  text-slate-100 font-semibold text-lg rounded-lg transition-all duration-[0.4s] shadow-md hover:scale-110 hover:shadow-xl"
              >
                {isLoading ? "Logging in..." : "Login"}
              </button>
            </form>
              </div>
              </div>
        </div>
      )}
            
    </div>
  );
}
