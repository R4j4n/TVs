"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

export function VideoPreview({ host, isPlaying, isPaused }) {
  const [isExpanded, setIsExpanded] = useState(false);
  return (
    <div>



<div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded((prev) => !prev)}
        >
        <p className="font-medium">Video Preview</p>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4" />
        ) : (
          <ChevronDown className="h-4 w-4" />
        )}
      </div>

      {isExpanded && (
    <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
      {isPlaying && !isPaused ? (
        <video
        key={`${host}-preview`}
        src={`http://${host}:8000/preview`}
        autoPlay
        controls
        muted
        className="w-full h-full object-contain" // Changed from object-cover
        style={{ maxHeight: '100%' }}
        />
      ) : (
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-500">No video playing</p>
        </div>
      )}
    </div>
      ) }

      </div>
  );
}