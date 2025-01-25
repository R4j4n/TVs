"use client";

import React, { useState, useEffect } from "react";
import {
  fetchAllDevices,
  getCurrentActiveDevice,
  rescanDevices,
  switchDevice,
} from "@/lib/api";

const TVList = () => {
  const [devices, setDevices] = useState([]);
  const [currentDevice, setCurrentDevice] = useState(null);
  const [loading, setLoading] = useState(true);
  const host = process.env.NEXT_PUBLIC_ACTIVE_SERVER_HOSTNAME;

  // Fetch devices list
  const fetchDevices = async () => {
    try {
      const data = await fetchAllDevices(host);
      // Filter out device 0
      setDevices(data.devices.filter((device) => device.number !== 0));
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch devices:", error);
      setLoading(false);
    }
  };

  // Fetch current active device
  const fetchCurrentDevice = async () => {
    try {
      const data = await getCurrentActiveDevice(host);
      setCurrentDevice(data.current_input);
    } catch (error) {
      console.error("Failed to fetch current device:", error);
    }
  };

  // Rescan devices
  const handleRescan = async () => {
    try {
      setLoading(true);
      const data = await rescanDevices(host);
      setDevices(data.devices.filter((device) => device.number !== 0));
      setLoading(false);
    } catch (error) {
      console.error("Rescan failed:", error);
      setLoading(false);
    }
  };

  // Switch device
  const handleDeviceSwitch = async (deviceNumber) => {
    try {
      await switchDevice(host, deviceNumber);
      fetchCurrentDevice();
    } catch (error) {
      console.error("Device switch failed:", error);
    }
  };

  // Initial and periodic device fetching
  useEffect(() => {
    fetchDevices();
    fetchCurrentDevice();

    // Periodic check for current device every 30 seconds
    const intervalId = setInterval(fetchCurrentDevice, 30000);

    // Cleanup interval on component unmount
    return () => clearInterval(intervalId);
  }, [host]);

  if (loading) return <div>Loading devices...</div>;

  return (
    <div className="space-y-4 pb-10">
      <h2 className="text-lg text-left pt-10 font-semibold">
        Connected Devices
      </h2>
      {currentDevice && (
        <div className="mt-4 text-sm text-left py-0 my-0 text-gray-600">
          Current Active Device: {currentDevice}
        </div>
      )}
      <div className="space-y-2">
        {devices.map((device) => (
          <div
            key={device.number}
            className={`flex items-center space-x-2 p-2 border rounded ${
              currentDevice === device.number
                ? "bg-green-100"
                : "hover:bg-gray-100"
            }`}
          >
            <input
              type="radio"
              id={`device-${device.number}`}
              name="deviceSwitch"
              checked={currentDevice === device.number}
              onChange={() => handleDeviceSwitch(device.number)}
            />
            <label htmlFor={`device-${device.number}`}>
              {device.name} (Device {device.number})
            </label>
          </div>
        ))}
      </div>
      <div className="mt-4">
        <button
          onClick={handleRescan}
          className="w-[75%] bg-gray-800 text-gray-200 py-2 rounded-xl hover:bg-black hover:text-white transition-colors duration-100"
        >
          Rescan Devices
        </button>
      </div>
    </div>
  );
};

export default TVList;
