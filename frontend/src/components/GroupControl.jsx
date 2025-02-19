// components/GroupControl.jsx
import { useState, useEffect } from 'react';
import { CardWrapper } from './PiCard/CardWrapper';
import { VideoControls } from './PiCard/VideoControls';
import { VideoList } from './PiCard/VideoList';
import { deleteVideo, fetchPiStatus, isTVOn, pauseVideo, playVideo, stopVideo, uploadVideo } from '@/lib/api';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { GroupHDMIStatus } from './GroupHDMIStatus';

export function GroupControl({ group }) {
  const [deviceStatuses, setDeviceStatuses] = useState({});
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [currentVideo, setCurrentVideo] = useState(null); 

  const fetchAllStatuses = async () => {
    try {
      const statuses = {};
      await Promise.all(
        group.devices.map(async (device) => {
          try {
            const status = await fetchPiStatus(device.host);
            const tvStatus = await isTVOn(device.host);
            statuses[device.host] = { status, tvStatus, error: null };
          } catch (err) {
            statuses[device.host] = { 
              status: null, 
              tvStatus: false, 
              error: 'Failed to fetch status' 
            };
          }
        })
      );
      setDeviceStatuses(statuses);
    } catch (err) {
      setError('Failed to fetch device statuses');
    }
  };

  useEffect(() => {
    fetchAllStatuses();
    const interval = setInterval(fetchAllStatuses, 60000);
    return () => clearInterval(interval);
  }, [group]);

  const handleGroupAction = async (actionType, ...args) => {
    try {
      switch (actionType) {
        case 'upload': {
          const file = args[0];

          const uploadPromises = group.devices.map(async device => {
            try {
              await uploadVideo(device.host, file);
              return { device: device.name, success: true };
            } catch (err) {
              return { device: device.name, success: false, error: err.message };
            }
          });

          const results = await Promise.all(uploadPromises);
          const failures = results.filter(r => !r.success);
          
          if (failures.length > 0) {
            const failureMessages = failures.map(f => `${f.device}: ${f.error}`).join('\n');
            throw new Error(`Upload failed for some devices:\n${failureMessages}`);
          }
          break;
        }
        case 'play': {
          const videoName = args[0];
          await Promise.all(
            group.devices.map(device => playVideo(device.host, videoName))
          );
          setCurrentVideo(videoName); 
          break;
        }
        case 'stop': {
          await Promise.all(
            group.devices.map(device => {stopVideo(device.host); console.log("Stopping the video for: ", device.host);})
          );
          setCurrentVideo(null); 
          break;
        }
        case 'delete': {
          const videoName = args[0];
          await Promise.all(
            group.devices.map(device => deleteVideo(device.host, videoName))
          );
          break;
        }
        case 'pause': {
          await Promise.all(
            group.devices.map(device => pauseVideo(device.host))
            
          );
          break;
        }
        default:
          console.warn('Unknown action type:', actionType);
          return;        
      }
      await fetchAllStatuses();
      setError(null);
    } catch (err) {
      console.error('Group action error:', err);
      setError(err.message || 'Failed to perform action on all devices');
      setTimeout(() => setError(null), 5000);
    }
  };

  const aggregateStatus = {
    isActive: Object.values(deviceStatuses).every(({ status }) => status),
    is_playing: Object.values(deviceStatuses).some(({ status }) => status?.is_playing),
    is_paused: Object.values(deviceStatuses).some(({ status }) => status?.is_paused),
    available_videos: Object.values(deviceStatuses).reduce((videos, { status }) => {
      if (status?.available_videos) {
        return [...new Set([...videos, ...status.available_videos])];
      }
      return videos;
    }, [])
  };

  return (
    <CardWrapper
      isGroup={true}
      title={group.name}
      status={Object.values(deviceStatuses).some(({ status }) => status)}
      error={error}
      tvStatus={false}
    >
    {error && (
      <Alert variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )}

    <div className="space-y-4">

      <VideoControls
        isGroup
        host={group.devices[0]?.host}
        status={aggregateStatus}
        uploading={uploading}
        setUploading={setUploading}
        onAction={handleGroupAction}
      />

      <VideoList
        isGroup
        host={group.devices[0]?.host}
        videos={aggregateStatus.available_videos}
        uploaded_on={[]}
        current_video={currentVideo} // Update this line
        is_playing={aggregateStatus.is_playing}
        is_paused={aggregateStatus.is_paused}
        onAction={handleGroupAction}
        groupDevices={group.devices}
      />

      <GroupHDMIStatus devices={group.devices} />
        
        
      <div className="mt-4">
          <h3 className="font-medium mb-2">Group Devices</h3>
          <div className="space-y-2">
            {group.devices.map((device) => {
              const deviceStatus = deviceStatuses[device.host];
              return (
                <div
                  key={device.host}
                  className={`p-2 rounded ${
                    deviceStatus?.status ? 'bg-green-100' : 'bg-red-100'
                  }`}
                >
                  <span className="font-medium">{device.name}</span>
                  {deviceStatus?.error && (
                    <span className="text-red-500 text-sm ml-2">
                      {deviceStatus.error}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </CardWrapper>
  );
}