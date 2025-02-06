// components/PiCard/currentHDMI.jsx

"use client";

import { getCurrentActiveDevice } from '@/lib/api';
import React from 'react'
import { useState, useEffect } from 'react';


const CurrentHDMI = () => {
    const host = process.env.NEXT_PUBLIC_ACTIVE_SERVER_HOSTNAME;


    const fetchCurrentDevice = async () => {
        try {
          const data = await getCurrentActiveDevice(host);
          setCurrentDevice(data?.current_input);
        } catch (error) {
          console.error("Failed to fetch current device:", error);
        }
      };


    useEffect(() => {
        fetchCurrentDevice();
        // Periodic check for current device every 30 seconds
        const intervalId = setInterval(fetchCurrentDevice, 60000);
        // Cleanup interval on component unmount
        return () => clearInterval(intervalId);
      }, [host]);


const [currentDevice, setCurrentDevice] = useState(null);
 
    return (
    <div>
        <h3>
        Current HDMI : {currentDevice}
        </h3>
        
        </div>
  )
}

export default CurrentHDMI