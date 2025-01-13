import { Play, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { playVideo, deleteVideo } from '@/lib/api'

export function VideoList({ host, videos, onAction }) {
  const handleDelete = async (videoName) => {
    if (!confirm(`Are you sure you want to delete ${videoName}?`)) return
    
    try {
      await deleteVideo(host, videoName)
      onAction()
    } catch (error) {
      console.error('Failed to delete video:', error)
    }
  }

  if (!videos.length) return null

  return (
    <div className="space-y-2">
      <p className="font-medium">Available Videos</p>
      <div className="space-y-1">
        {videos.map((video) => (
          <div key={video} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
            <span className="text-sm truncate flex-1">{video}</span>
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={async () => {
                  await playVideo(host, video)
                  onAction()
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
    </div>
  )
}