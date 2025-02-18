// components/PiCard/VideoControls.jsx
import { useState, useEffect } from 'react'
import { Play, Square, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { playVideo, stopVideo, uploadVideo } from '@/lib/api'

export function VideoControls({
  host,
  status,
  uploading,
  setUploading,
  onAction,
  isGroup = false
}) {
  const [uploadError, setUploadError] = useState('');
  const [showMessage, setShowMessage] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    setIsPlaying(status?.is_playing ?? false);
    setIsPaused(status?.is_paused ?? false);
  }, [status]);

  const availableVideos = status?.available_videos ?? [];

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      setUploadError('No file selected');
      return;
    }
    setUploadError('');
    const maxSize = 500 * 1024 * 1024;
    if (file.size > maxSize) {
      setUploadError('File size too large. Maximum size is 500MB.');
      return;
    }

    const validTypes = ['video/mp4', 'video/webm', 'video/ogg'];
    if (!validTypes.includes(file.type)) {
      setUploadError('Invalid file type. Please upload MP4, WebM, or OGG video files.');
      return;
    }
    setUploading(true);
    try {
      if (isGroup) {
        await onAction('upload', file);
      } else {
        await uploadVideo(host, file);
        onAction();
      }
      setShowMessage(true);
      setTimeout(() => setShowMessage(false), 3000);
    } catch (err) {
      console.error('Upload failed:', err);
      setUploadError(err.message || 'Failed to upload video. Please try again.');
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  }

  const handlePlay = async () => {
    if (availableVideos[0]) {
      await playVideo(host, availableVideos[0]);
      setIsPlaying(true);
      onAction("play");
    }
  }

  const handleStop = async () => {
    await stopVideo(host);
    setIsPlaying(false);
    setIsPaused(false);
    onAction("stop");
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex gap-2">
        {isPlaying || isPaused ? (
          <Button 
            variant="destructive" 
            onClick={handleStop}
            className="flex-1"
          >
            <Square className="h-4 w-4 mr-2" />
            Stop
          </Button>
        ) : (
          <Button
            variant="default"
            onClick={handlePlay}
            disabled={availableVideos.length === 0}
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

      {(showMessage || uploadError) && (
        <div className={`${
          uploadError ? 'bg-red-600' : 'bg-emerald-600'
        } text-white p-2 rounded shadow-md mt-2`}>
          {uploadError || 'File uploaded successfully!'}
        </div>
      )}
    </div>
  )
}