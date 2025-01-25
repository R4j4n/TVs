"use client";

import { useState } from "react";
import Schedule from "./Schedule";
import TVList from "./TVList";
import { ChevronDown, ChevronUp } from "lucide-react";

const Settings = ({ host }) => {
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
          <TVList/>
          <Schedule host={host} />
        </div>
      )}
    </div>
  );
};

export default Settings;
