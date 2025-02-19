// components/PiCard/Settings/index.jsx

"use client";

import { useState } from "react";
import Schedule from "./Schedule";
import { ChevronDown, ChevronUp } from "lucide-react";
import HDMIManager from "./HDMIManager";

const Settings = ({ host, status }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div>
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded((prev) => !prev)}
      >
        <p className="font-medium">Advanced Settings</p>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4" />
        ) : (
          <ChevronDown className="h-4 w-4" />
        )}
      </div>
      {isExpanded && (
        <div>
          <HDMIManager host={host} />
          {status && (
            <Schedule host={host} />
          )}
        </div>
      )}
    </div>
  );
};

export default Settings;
