export function VideoPreview({ host, isPlaying }) {
  return (
    <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
      {isPlaying ? (
        <video
          src={`http://${host}:8000/preview`}
          autoPlay
          muted
          loop
          className="w-full h-full object-cover"
        >
          Your browser does not support the video tag.
        </video>
      ) : (
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-500">No video playing</p>
        </div>
      )}
    </div>
  );
}
