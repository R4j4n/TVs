import { useState, useEffect, useRef } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { getBaseUrl } from "@/lib/api"; // Make sure to import getBaseUrl from your api.js

export function VideoPreview({ host, isPlaying, isPaused, authKey }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);
  const videoRef = useRef(null);

  useEffect(() => {
    if (isPlaying && !isPaused && isExpanded) {
      const auth_token = sessionStorage.getItem("authToken");
      const setupVideoStream = async () => {
        try {
          // Use getBaseUrl() to construct the URL
          const response = await fetch(`${getBaseUrl()}/pi/${host}/preview`, {
            headers: {
              'AUTH': auth_token,
              'skip_zrok_interstitial': '1'
            }
          });

          if (!response.ok) {
            throw new Error('Failed to fetch video stream');
          }

          // Create a blob URL from the response
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          setVideoUrl(url);

          return () => {
            if (url) {
              URL.revokeObjectURL(url);
            }
          };
        } catch (error) {
          console.error('Error fetching video stream:', error);
        }
      };

      setupVideoStream();

      // Cleanup function
      return () => {
        if (videoUrl) {
          URL.revokeObjectURL(videoUrl);
        }
      };
    }
  }, [host, isPlaying, isPaused, isExpanded, authKey]);

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
              ref={videoRef}
              key={`${host}-preview-${videoUrl}`}
              src={videoUrl}
              autoPlay
              controls
              muted
              className="w-full h-full object-contain"
              style={{ maxHeight: '100%' }}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500">No video playing</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}