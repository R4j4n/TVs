"use client";

import { useState } from "react";
import { CardWrapper } from "./CardWrapper";
import { VideoPreview } from "./VideoPreview";
import { VideoControls } from "./VideoControls";
import { VideoList } from "./VideoList";
import { useStatus } from "@/hooks/useStatus";
import Schedule from "./Schedule";
import TVOnStatus from "./TVOnStatus";

export function PiCard({ pi }) {
  const [uploading, setUploading] = useState(false);
  const { status, error, refreshStatus } = useStatus(pi.host);

  return (
    <CardWrapper
      pi={pi}
      status={status}
      error={error}
      onRefresh={refreshStatus}
    >
      <VideoPreview host={pi.host} isPlaying={status?.is_playing} />
      <VideoControls
        host={pi.host}
        status={status}
        uploading={uploading}
        setUploading={setUploading}
        onAction={refreshStatus}
      />
      <VideoList
        host={pi.host}
        videos={status?.available_videos || []}
        uploaded_on={status?.date_uploaded || []}
        onAction={refreshStatus}
        current_video={status?.current_video}
        isPlaying={status?.is_playing}
        
      />
      <Schedule host={pi.host} isLooping = {status?.is_looping} />
    </CardWrapper>
  );
}
