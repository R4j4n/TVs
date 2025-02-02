// components/PiCard/VideoControls.jsx
import { useState } from 'react'
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

  // Safely access status properties
  const isPlaying = status?.is_playing ?? false;
  const isPaused = status?.is_paused ?? false;
  const availableVideos = status?.available_videos ?? [];

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      setUploadError('No file selected');
      return;
    }

    // Clear any previous errors
    setUploadError('');

    // Check file size (example: limit to 500MB)
    const maxSize = 500 * 1024 * 1024; // 500MB in bytes
    if (file.size > maxSize) {
      setUploadError('File size too large. Maximum size is 500MB.');
      return;
    }

    // Check file type
    const validTypes = ['video/mp4', 'video/webm', 'video/ogg'];
    if (!validTypes.includes(file.type)) {
      setUploadError('Invalid file type. Please upload MP4, WebM, or OGG video files.');
      return;
    }

    setUploading(true);
    try {
      if (isGroup) {
        console.log('Starting group upload for file:', file.name); // Debug log
        await onAction('upload', file);
      } else {
        console.log('Starting single upload for file:', file.name); // Debug log
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
      // Reset the input
      event.target.value = '';
    }
  }

  return (
    <div className="flex flex-col gap-2">
    <div className="flex gap-2">
    {isPlaying && !isPaused ? (
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
    ) : isPaused ? (
      <Button 
        variant="default"
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
          if (availableVideos[0]) {
            await playVideo(host, availableVideos[0])
            onAction()
          }
        }}
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