"use client";

import { useState } from "react";
import { CardWrapper } from "./CardWrapper";
import { VideoPreview } from "./VideoPreview";
import { VideoControls } from "./VideoControls";
import { VideoList } from "./VideoList";
import { useStatus } from "@/hooks/useStatus";
import Settings from "./Settings";
import CurrentHDMI from "./currentHDMI";


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
      <CurrentHDMI/>
      <VideoControls
        host={pi.host}
        status={status}
        uploading={uploading}
        setUploading={setUploading}
        onAction={refreshStatus}
      />
      <VideoPreview 
        host={pi.host} 
        isPlaying={status?.is_playing} 
        isPaused={status?.is_paused} 
      />
      <VideoList
        host={pi.host}
        videos={status?.available_videos || []}
        uploaded_on={status?.date_uploaded || []}
        onAction={refreshStatus}
        current_video={status?.current_video}
        is_playing={status?.is_playing}
        is_paused={status?.is_paused}       
      />
      <Settings host={pi.host} />
    </CardWrapper>
  );
}
