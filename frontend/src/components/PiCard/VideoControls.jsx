'use client'

import { Play, Square, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { playVideo, stopVideo, uploadVideo } from '@/lib/api'

export function VideoControls({
  host,
  status,
  uploading,
  setUploading,
  onAction
}) {
  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    try {
      await uploadVideo(host, file)
      onAction()
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  return (
    <div className="flex gap-2">
      {status?.is_playing ? (
        <Button 
          variant="destructive" 
          onClick={async () => {
            await stopVideo(host)
            onAction()
          }}
          className="flex-1"
        >
          <Square className="h-4 w-4 mr-2" />
          Stop
        </Button>
      ) : (
        <Button
          variant="default"
          onClick={async () => {
            if (status?.available_videos[0]) {
              await playVideo(host, status.available_videos[0])
              onAction()
            }
          }}
          disabled={!status?.available_videos.length}
          className="flex-1"
        >
          <Play className="h-4 w-4 mr-2" />
          Play
        </Button>
      )}
      
      <Button 
        variant="outline" 
        className="flex-1"
        onClick={() => document.getElementById(`upload-${host}`)?.click()}
        disabled={uploading}
      >
        <Upload className="h-4 w-4 mr-2" />
        {uploading ? 'Uploading...' : 'Upload'}
      </Button>
      <input
        type="file"
        id={`upload-${host}`}
        className="hidden"
        accept="video/*"
        onChange={handleFileUpload}
      />
    </div>
  )
}