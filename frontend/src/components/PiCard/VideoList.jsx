import { Play, Trash2, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { playVideo, deleteVideo } from "@/lib/api";
import { useState } from "react";

export function VideoList({ host, videos, uploaded_on, onAction, current_video }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const videoMap = videos.reduce((map, video, index) => {
    map[video] = uploaded_on[index];
    return map;
  }, {});

  const handleDelete = async (videoName) => {
    if (!confirm(`Are you sure you want to delete ${videoName}?`)) return;

    try {
      await deleteVideo(host, videoName);
      onAction();
    } catch (error) {
      console.error("Failed to delete video:", error);
    }
  };

  if (!videos.length) return null;

  return (
    <div className="space-y-2">
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded((prev) => !prev)}
      >
        <p className="font-medium">Available Videos ({videos.length})</p>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4" />
        ) : (
          <ChevronDown className="h-4 w-4" />
        )}
      </div>

      {isExpanded && (
        <div className="space-y-1">
          {videos.map((video) => (
            <div
              key={video}
              className={`flex items-center justify-between p-2 ${video===current_video ?  "bg-gradient-to-t from-emerald-800 to-emerald-600 text-slate-200" : "bg-gray-100"} rounded-lg`}
            >
              <span className="text-sm truncate flex-1"> {video} <br/>  <span className= {"text-xs"}>Upload: { videoMap[video] }</span> </span>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={async () => {
                    await playVideo(host, video);
                    onAction();
                  }}
                >
                  <Play className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDelete(video)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
