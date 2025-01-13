"use client";

import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

const Schedule = ({}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="space-y-2">
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded((prev) => !prev)}
      >
        <p className="font-medium">Schedule</p>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4" />
        ) : (
          <ChevronDown className="h-4 w-4" />
        )}
      </div>

      {isExpanded && (
        <div className="pt-4">Here will be the schedule selector</div>
      )}
    </div>
  );
};

export default Schedule;
