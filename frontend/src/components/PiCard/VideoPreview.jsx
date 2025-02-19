import { useState, useEffect, useRef } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

export function VideoPreview({ host, isPlaying, isPaused, authKey }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);
  const videoRef = useRef(null);

  useEffect(() => {
    if (isPlaying && !isPaused && isExpanded) {
      const auth_token = sessionStorage.getItem("authToken");
      const setupVideoStream = async () => {
        try {
          const response = await fetch(`http://${host}:8000/preview`, {
            headers: {
              'AUTH': auth_token
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