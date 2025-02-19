// hooks/useStatus.jsx

import { useState, useEffect } from "react";
import { fetchPiStatus, getCurrentActiveDevice, isTVOn } from "@/lib/api";

export function useStatus(host) {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [tvStatus, setTVStatus] = useState(null);
  const [currentActivePort, setCurrentActivePort] = useState(null);

  const refreshStatus = async () => {
    try {
      const data = await fetchPiStatus(host);
      const tvStatus = await isTVOn(host);
      const current_device_number = await getCurrentActiveDevice(host);
      console.log("Current active device number: ", current_device_number.current_input);
      setCurrentActivePort(current_device_number.current_input);
      setStatus(data);
      setTVStatus(tvStatus);
      setError(null);
    } catch (err) {
      setError("Failed to fetch status");
    }
  };

  useEffect(() => {
    refreshStatus();
    const interval = setInterval(refreshStatus, 60000);
    return () => clearInterval(interval);
  }, [host]);

  return { status, error, tvStatus, refreshStatus, currentActivePort };
}
