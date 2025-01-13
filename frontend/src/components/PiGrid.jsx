'use client'

import { useState, useEffect } from 'react'
import { PiCard } from './PiCard'

export function PiGrid() {
  const [pis, setPis] = useState([])
  
  useEffect(() => {
    // In production, replace with actual Zeroconf discovery
    setPis([
      { name: "Living Room Pi", host: "10.51.213.217" },
      { name: "Prajwal", host: "10.51.200.68" },
      { name: "Bedroom Pi", host: "192.168.1.102" },
      { name: "Office Pi", host: "192.168.1.103" }
    ])
  }, [])

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      {pis.map((pi) => (
        <PiCard key={pi.host} pi={pi} />
      ))}
    </div>
  )
}