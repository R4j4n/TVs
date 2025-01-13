'use client'

import { useState } from 'react'
import { CardWrapper } from './CardWrapper'
import { VideoPreview } from './VideoPreview'
import { VideoControls } from './VideoControls'
import { VideoList } from './VideoList'
import { useStatus } from '@/hooks/useStatus'

export function PiCard({ pi }) {
  const [uploading, setUploading] = useState(false)
  const { status, error, refreshStatus } = useStatus(pi.host)

  return (
    <CardWrapper pi={pi} error={error} onRefresh={refreshStatus}>
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
        onAction={refreshStatus}
      />
    </CardWrapper>
  )
}