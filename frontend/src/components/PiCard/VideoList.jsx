import { Play, Pause, Trash2, ChevronDown, ChevronUp, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { playVideo, deleteVideo, pauseVideo } from "@/lib/api";
import { useState } from "react";

export function VideoList({
  host,
  videos = [],
  uploaded_on = [],
  onAction,
  current_video,
  is_playing,
  is_paused,
  isGroup = false,
  groupDevices = []
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [videoToDelete, setVideoToDelete] = useState(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState({});


  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-emerald-600" />
      </div>
    );
  }
 


  // Simplified videoMap creation with debug logs
  const videoMap = Array.isArray(videos) ? videos.reduce((map, video, index) => {
      map[video] = uploaded_on[index];
      const date = uploaded_on[index];
      map[video] = date;
    return map;
  }, {}) : {};


  const handleDelete = async () => {
    if (!videoToDelete) return;
    setActionLoading({ [videoToDelete]: true });

    try {
      if (isGroup) {
        await onAction('delete', videoToDelete); 
      } else {
        await deleteVideo(host, videoToDelete);
        onAction();
      }
    } catch (error) {
      console.error("Failed to delete video:", error);
    } finally {
      setShowModal(false);
      setVideoToDelete(null);
      setActionLoading({});
    }
  };

  const handleVideoPause = async () => {
    setActionLoading({ [current_video]: true });
    try {
      if (isGroup) {
        await onAction('pause'); 
      } else {
        await pauseVideo(host);
        onAction();
      }
    } catch (error) {
      console.error("Unable to pause the video", error);
    } finally {
      setActionLoading({});
    }
  };

  const handleVideoPlay = async (video) => {
    setActionLoading({ [video]: true });
    try {
      if (isGroup) {
        await onAction('play', video); 
      } else {
        await playVideo(host, video);
        onAction();
      }
    } catch (error) {
      console.error("Unable to play video", error);
    } finally {
      setActionLoading({});
    }
  };

  if (!Array.isArray(videos) || videos.length === 0) return null;

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
              className={`flex items-center justify-between p-2 ${
                video === current_video
                  ? "bg-gradient-to-t from-emerald-800 to-emerald-600 text-slate-200"
                  : "bg-gray-100"
              } rounded-lg`}
            >
              <span className="text-sm truncate flex-1">
                {video} <br />
                <span className={"text-xs"}>Upload: {videoMap[video]}</span>
              </span>
              <div className="flex gap-2">
                {actionLoading[video] ? (
                  <Button
                    variant="ghost"
                    size="icon"
                    disabled
                  >
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  </Button>
                ) : video === current_video && is_playing && !is_paused ? (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleVideoPause}
                  >
                    <Pause className="h-4 w-4" />
                  </Button>
                ) : (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleVideoPlay(video)}
                  >
                    <Play className="h-4 w-4" />
                  </Button>
                )}

                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => {
                    setVideoToDelete(video);
                    setShowModal(true);
                  }}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-rose-900 bg-opacity-30 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-80">
            <h2 className="text-lg font-semibold">Confirm Deletion</h2>
            <p className="text-sm text-gray-600 my-4">
              Are you sure you want to delete <b>{videoToDelete}</b>?
            </p>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowModal(false)}>
                Cancel
              </Button>
              <Button 
                variant="destructive" 
                onClick={handleDelete}
                disabled={actionLoading[videoToDelete]}
              >
                {actionLoading[videoToDelete] ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  'Delete'
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}