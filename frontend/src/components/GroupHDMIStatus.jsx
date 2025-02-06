// components/GroupHDMIStatus.jsx
import { useState, useEffect } from 'react';
import { getCurrentActiveDevice, fetch_hdmi_map, switchDevice } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp } from 'lucide-react';

export function GroupHDMIStatus({ devices }) {
  const [deviceStatuses, setDeviceStatuses] = useState({});
  const [hdmiMaps, setHdmiMaps] = useState({});
  const [isExpanded, setIsExpanded] = useState(false);

  const fetchAllStatuses = async () => {
    const statuses = {};
    const maps = {};
    
    await Promise.all(
      devices.map(async (device) => {
        try {
          const currentDevice = await getCurrentActiveDevice(device.host);
          const hdmiMap = await fetch_hdmi_map(device.host);
          statuses[device.host] = currentDevice?.current_input;
          maps[device.host] = hdmiMap;
        } catch (err) {
          console.error(`Failed to fetch status for ${device.name}:`, err);
        }
      })
    );

    setDeviceStatuses(statuses);
    setHdmiMaps(maps);
  };

  useEffect(() => {
    fetchAllStatuses();
    const interval = setInterval(fetchAllStatuses, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleDeviceSwitch = async (host, port) => {
    try {
      await switchDevice(host, port);
      await fetchAllStatuses();
    } catch (err) {
      console.error('Failed to switch device:', err);
    }
  };

  return (
    <div className="space-y-2">
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <p className="font-medium">HDMI Status</p>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4" />
        ) : (
          <ChevronDown className="h-4 w-4" />
        )}
      </div>

      {isExpanded && (
        <div className="space-y-4">
          {devices.map((device) => {
            const currentPort = deviceStatuses[device.host];
            const hdmiMap = hdmiMaps[device.host] || {};

            return (
              <div
                key={device.host}
                className="p-4 bg-gray-50 rounded-lg space-y-2"
              >
                <div className="flex justify-between items-center">
                  <h3 className="font-medium">{device.name}</h3>
                  <span className="text-sm text-gray-600">
                    Current: Port {currentPort}
                  </span>
                </div>
                <div className="flex gap-2 flex-wrap">
                  {Object.entries(hdmiMap).map(([port, deviceName]) => (
                    <Button
                      key={port}
                      variant={currentPort === parseInt(port) ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleDeviceSwitch(device.host, port)}
                    >
                      {deviceName} (Port {port})
                    </Button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}