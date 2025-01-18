"use client";

import { useState, useEffect } from "react";
import { PiCard } from "./PiCard";
import { fetchPis } from "@/lib/api";



export function PiGrid() {

  const [pis, setPis] = useState([])  // Array to store the results
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadPis() {
      try {
        const result = await fetchPis(process.env.NEXT_PUBLIC_ACTIVE_SERVER_HOSTNAME)
        // Ensure result is an array, if not, convert or handle accordingly
        setPis(Array.isArray(result) ? result : Object.values(result))
      } catch (err) {
        console.error('Failed to fetch Pis:', err)
        setError('Failed to load Pis')
      }
    }

    loadPis()
  }, [])

  if (error) return <p>{error}</p>




  // useEffect(() => {
  //   // dummy values for testing . . . . . 
  //   setPis([
  //     { name: "Living Room Pi", host: "10.51.213.217" },
  //     { name: "Prajwal", host: "10.51.200.68" },
  //     { name: "Bedroom Pi", host: "192.168.1.102" },
  //     { name: "Office Pi", host: "192.168.1.103" },
  //   ]);
  // }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      {pis.map((pi) => (
        <PiCard key={pi.host} pi={pi} />
      ))}
    </div>
  );
}
