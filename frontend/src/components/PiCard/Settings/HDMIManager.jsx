// components/PiCard/Settings/HDMIManager.jsx



import React, { useState, useEffect } from "react";
import { CheckCircle, XCircle, RefreshCw, Trash2 } from "lucide-react";
import {
  check_json,
  fetch_hdmi_map,
  getCurrentActiveDevice,
  reset_hdmi_map,
  set_hdmi_map,
  switchDevice,
} from "@/lib/api";

// Simplified Alert Component
const Alert = ({ children, className }) => (
  <div className={`p-4 rounded-lg ${className}`}>{children}</div>
);

const AlertDescription = ({ children, className }) => (
  <span className={`text-sm ${className}`}>{children}</span>
);

// Simplified Dialog Components
const Dialog = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div>
      {React.Children.map(children, (child) =>
        React.cloneElement(child, { isOpen, setIsOpen })
      )}
    </div>
  );
};

const DialogTrigger = ({ children, asChild, isOpen, setIsOpen }) => {
  return React.cloneElement(children, {
    onClick: () => setIsOpen(true),
  });
};

const DialogContent = ({ children, isOpen, setIsOpen }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        {React.Children.map(children, (child) => {
          if (typeof child.type === "string") {
            return child;
          }
          return React.cloneElement(child, { setIsOpen });
        })}
      </div>
    </div>
  );
};

const DialogHeader = ({ children, setIsOpen }) => {
  return (
    <div className="mb-4">
      {React.Children.map(children, (child) => {
        if (typeof child.type === "string") {
          return child;
        }
        return React.cloneElement(child, { setIsOpen });
      })}
    </div>
  );
};

const DialogTitle = ({ children }) => (
  <h2 className="text-lg font-semibold">{children}</h2>
);

// Simplified Select Components
const Select = ({ value, onValueChange, children }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      {React.Children.map(children, (child) =>
        React.cloneElement(child, {
          value,
          onValueChange,
          isOpen,
          setIsOpen,
        })
      )}
    </div>
  );
};

const SelectTrigger = ({ children, value, isOpen, setIsOpen }) => (
  <button
    className="w-full px-3 py-2 text-left border rounded-md flex justify-between items-center"
    onClick={() => setIsOpen(!isOpen)}
  >
    <span>{value}</span>
    <span className="ml-2">▼</span>
  </button>
);

const SelectContent = ({
  children,
  isOpen,
  value,
  onValueChange,
  setIsOpen,
}) => {
  if (!isOpen) return null;

  return (
    <div className="absolute w-full mt-1 bg-white border rounded-md shadow-lg z-10 max-h-60 overflow-auto">
      {React.Children.map(children, (child) =>
        React.cloneElement(child, {
          onSelect: (value) => {
            onValueChange(value);
            setIsOpen(false);
          },
          isSelected: child.props.value === value,
        })
      )}
    </div>
  );
};

const SelectItem = ({ children, value, onSelect, isSelected }) => (
  <div
    className={`px-3 py-2 cursor-pointer hover:bg-gray-100 ${
      isSelected ? "bg-gray-100" : ""
    }`}
    onClick={() => onSelect(value)}
  >
    {children}
  </div>
);

// Simplified Button Component
const Button = ({ children, className, onClick, variant, size }) => {
  let baseClasses = "px-4 py-2 rounded-md transition-colors";

  if (variant === "ghost") {
    baseClasses += " hover:bg-gray-100";
  } else if (variant === "outline") {
    baseClasses += " border border-gray-300 hover:bg-gray-50";
  }

  if (size === "icon") {
    baseClasses = "p-2 rounded-md hover:bg-gray-100";
  }

  return (
    <button className={`${baseClasses} ${className}`} onClick={onClick}>
      {children}
    </button>
  );
};

// Device Selection Radio Group Component
const DeviceRadioGroup = ({ devices, currentDevice, onDeviceSwitch }) => {

  if (!devices || Object.keys(devices).length === 0) {
    return <div>No devices configured</div>;
  }

  const handleChange = (port) => {
    onDeviceSwitch(port);
  };

  return (
    <div className="space-y-3">
      {Object.entries(devices).map(([port, device]) => (
        <div
          key={port}
          className={`flex items-center space-x-3 p-3 rounded-lg border transition-colors ${
            currentDevice === parseInt(port)
              ? "bg-emerald-50 border-emerald-600"
              : "hover:bg-gray-50 border-gray-200"
          }`}
        >
          <input
            type="radio"
            id={`port-${port}`}
            name="hdmiPort"
            value={port}
            checked={currentDevice === parseInt(port)}
            onChange={() => handleChange(port)}
            className="text-emerald-600 focus:ring-emerald-600"
          />
          <label
            htmlFor={`port-${port}`}
            className="flex-1 text-sm font-medium text-gray-900 cursor-pointer"
          >
            {device} (Port {port})
          </label>
        </div>
      ))}
    </div>
  );
};

const HDMIManager = ({ host }) => {
  const [jsonExists, setJsonExists] = useState(false);
  const [hdmiMap, setHdmiMap] = useState({});
  const [currentDevice, setCurrentDevice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");
  const [alertType, setAlertType] = useState("success");
  const [formData, setFormData] = useState({
    1: "Other",
    2: "Other",
    3: "Other",
  });

  const deviceOptions = ["Raspberry Pi", "TV", "Other"];

  const showNotification = (message, type) => {
    setAlertMessage(message);
    setAlertType(type);
    setShowAlert(true);
    setTimeout(() => setShowAlert(false), 3000);
  };

  const fetchHdmiMap = async () => {
    try {
      const data = await fetch_hdmi_map(host);
      setHdmiMap(data);
    } catch (error) {
      console.error("Failed to fetch HDMI mapping:", error);
      showNotification("Failed to fetch HDMI mapping", "error");
    }
  };

  const fetchCurrentDevice = async () => {
    try {
      const data = await getCurrentActiveDevice(host);
      setCurrentDevice(data.current_input);
    } catch (error) {
      console.error("Failed to fetch current device:", error);
    }
  };

  const checkJsonStatus = async () => {
    try {
      const exists = await check_json(host);
      setJsonExists(exists);
      if (exists) {
        await Promise.all([fetchHdmiMap(), fetchCurrentDevice()]);
      }
      return exists;
    } catch (error) {
      showNotification("Failed to check HDMI configuration", "error");
      return false;
    } finally {
      await fetchCurrentDevice();
      setLoading(false);
    }
  };

  const handleDeviceSwitch = async (portNumber) => {
    try {
      setLoading(true);
      await switchDevice(host, parseInt(portNumber));
      await fetchCurrentDevice();
      showNotification(
        `Successfully switched to port ${portNumber}`,
        "success"
      );
    } catch (error) {
      console.error("Switch error:", error);
      showNotification(`Failed to switch to port ${portNumber}`, "error");
    } finally {
      setLoading(false);
    }
  };

  const validateDeviceSelection = (newFormData) => {
    // Count how many Raspberry Pis are selected
    const raspberryPiCount = Object.values(newFormData).filter(
      (device) => device === "Raspberry Pi"
    ).length;

    return raspberryPiCount <= 1;
  };

  const handleFormSubmit = async () => {
    try {
      if (!validateDeviceSelection(formData)) {
        showNotification("Only one Raspberry Pi can be configured", "error");
        return;
      }

      setLoading(true);
      const response = await set_hdmi_map(host, formData);
      await checkJsonStatus();
      await fetchCurrentDevice();
      showNotification("HDMI configuration saved successfully", "success");
    } catch (error) {
      console.error("Error saving HDMI configuration:", error);
      showNotification("Failed to save HDMI configuration", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      setLoading(true);
      await reset_hdmi_map(host);
      showNotification("HDMI configuration reset successfully", "success");
      setJsonExists(false);
      setHdmiMap({});
      setCurrentDevice(null);
    } catch (error) {
      showNotification("Failed to reset configuration", "error");
    } finally {
      setLoading(false);
    }
  };

  const DialogActions = ({ setIsOpen }) => {
    return (
      <div className="flex justify-end gap-3 mt-4">
        <Button variant="outline" onClick={() => setIsOpen(false)}>
          Cancel
        </Button>
        <Button
          className="bg-rose-600 hover:bg-rose-700 text-white"
          onClick={() => {
            handleReset();
            setIsOpen(false);
          }}
        >
          Reset
        </Button>
      </div>
    );
  };

  useEffect(() => {
    checkJsonStatus();
  }, []);

  useEffect(() => {
    let interval;
    if (jsonExists) {
      interval = setInterval(fetchCurrentDevice, 30000);
    }
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [jsonExists]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-emerald-600" />
      </div>
    );
  }


  return (
    <div className="max-w-md mx-auto p-6 space-y-6">
      {showAlert && (
        <Alert
          className={`${
            alertType === "success"
              ? "bg-emerald-50 border-emerald-600"
              : "bg-rose-50 border-rose-600"
          } fixed top-4 right-4 w-96 transition-all duration-300 z-50`}
        >
          <div className="flex items-center gap-2">
            {alertType === "success" ? (
              <CheckCircle className="h-4 w-4 text-emerald-600" />
            ) : (
              <XCircle className="h-4 w-4 text-rose-600" />
            )}
            <AlertDescription
              className={
                alertType === "success" ? "text-emerald-600" : "text-rose-600"
              }
            >
              {alertMessage}
            </AlertDescription>
          </div>
        </Alert>
      )}

      {!jsonExists ? (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-gray-900">
            Configure HDMI Devices
          </h2>
          <div className="space-y-4">
            {[1, 2, 3].map((port) => (
              <div key={port} className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  HDMI Port {port}
                </label>
                <Select
                  value={formData[port]}
                  onValueChange={(value) => {
                    const newFormData = { ...formData, [port]: value };
                    // If selecting Raspberry Pi, check if one already exists
                    if (value === "Raspberry Pi") {
                      const existingRPiPort = Object.entries(formData).find(
                        ([p, device]) =>
                          p !== port.toString() && device === "Raspberry Pi"
                      );
                      if (existingRPiPort) {
                        showNotification(
                          `Raspberry Pi is already configured on Port ${existingRPiPort[0]}`,
                          "error"
                        );
                        return;
                      }
                    }
                    setFormData(newFormData);
                  }}
                >
                  <SelectTrigger>{formData[port]}</SelectTrigger>
                  <SelectContent>
                    {deviceOptions.map((option) => (
                      <SelectItem key={option} value={option}>
                        {option}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            ))}
            <Button
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white"
              onClick={handleFormSubmit}
            >
              Save Configuration
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">
              HDMI Devices
            </h2>
            <Dialog>
              <DialogTrigger asChild>
                <Button variant="ghost" size="icon">
                  <Trash2 className="h-5 w-5 text-rose-600" />
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Reset HDMI Configuration</DialogTitle>
                </DialogHeader>
                <p className="text-gray-600">
                  Are you sure you want to reset the HDMI configuration? This
                  action cannot be undone.
                </p>
                <DialogActions />
              </DialogContent>
            </Dialog>
          </div>

          {currentDevice && (
            <div className="text-sm text-gray-600 mt-4">
              Current Active Device: Port {currentDevice}
            </div>
          )}

          <div className="mt-4">
            {Object.keys(hdmiMap).length > 0 ? (
              <DeviceRadioGroup
                devices={hdmiMap}
                currentDevice={currentDevice}
                onDeviceSwitch={handleDeviceSwitch}
              />
            ) : (
              <div className="text-gray-600">Loading devices...</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default HDMIManager;
