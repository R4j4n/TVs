// hooks/useStatus.jsx

import { useState, useEffect } from "react";
import { fetchPiStatus, isTVOn } from "@/lib/api";

export function useStatus(host) {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [tvStatus, setTVStatus] = useState(null);

  const refreshStatus = async () => {
    try {
      const data = await fetchPiStatus(host);
      const tvStatus = await isTVOn(host);
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

  return { status, error, tvStatus, refreshStatus };
}
