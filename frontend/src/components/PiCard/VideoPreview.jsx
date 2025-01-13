export function VideoPreview({ host, isPlaying }) {
    return (
      <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
        {isPlaying ? (
          <img 
            src={`http://${host}:8000/preview`} 
            alt="Video Preview"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500">No video playing</p>
          </div>
        )}
      </div>
    )
  }