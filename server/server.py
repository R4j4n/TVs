import json
import logging
import os
import shutil
import socket
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

import netifaces
import uvicorn
import vlc
from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from utils.ffmpeg_compressor import VideoCompressor
from zeroconf import ServiceInfo, Zeroconf

from routers.cec_list_hdmi import router_cec as cec_routers
from routers.control_tv import tv_controller


class PlayerState(str, Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    NO_MEDIA = "no_media"


class VideoManager:
    def __init__(self):
        self.upload_dir = Path("uploaded_videos")
        self.compressed_dir = self.upload_dir / "compressed"
        self.upload_dir.mkdir(exist_ok=True)
        self.compressed_dir.mkdir(exist_ok=True)
        self.last_played_file = Path("last_played.json")
        self.error_count = 0
        self.max_retry_attempts = 3
        self.retry_delay = 1
        self.current_video = None
        self.is_playing = False

        self.setup_vlc()
        self.load_last_played()
        self.compressor = VideoCompressor(target_resolution=240, target_fps=10)

    def setup_vlc(self):
        """Initialize VLC with robust settings"""
        try:
            vlc_args = [
                "--no-video-title-show",  # Hide title
                "--fullscreen",  # Force fullscreen
                "--mouse-hide-timeout=0",  # Hide mouse
                "--no-quiet",  # Show errors
                "--no-xlib",  # Better compatibility
                "--aout=alsa",  # Stable audio output
                "--file-logging",  # Enable logging
                "--logfile=vlc_log.txt",  # Log file
            ]

            self.instance = vlc.Instance(*vlc_args)
            self.media_list = self.instance.media_list_new()
            self.list_player = self.instance.media_list_player_new()
            self.list_player.set_media_list(self.media_list)
            self.list_player.set_playback_mode(vlc.PlaybackMode.loop)

            # Get the underlying media player for more control
            self.player = self.list_player.get_media_player()
            self.player.audio_set_volume(100)

            logger.info("VLC setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to setup VLC: {e}")
            raise RuntimeError(f"Failed to initialize video player: {e}")

    def validate_video(self, video_path: str) -> bool:
        """Validate video file before playing"""
        try:
            test_media = self.instance.media_new(video_path)
            test_media.parse()
            duration = test_media.get_duration()

            if duration <= 0:
                logger.error(f"Invalid video duration: {duration}ms")
                return False

            # Check if file is readable
            with open(video_path, "rb") as f:
                f.seek(0, 2)  # Seek to end to verify file is readable

            logger.info(f"Video validation successful: {video_path}")
            return True

        except Exception as e:
            logger.error(f"Video validation failed: {e}")
            return False

    def load_video(self, video_path: str):
        if not Path(video_path).is_file():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if not self.validate_video(video_path):
            raise ValueError("Invalid video file")

        try:
            self.media_list = self.instance.media_list_new()
            media = self.instance.media_new(video_path)
            media.parse()  # Wait for media to be parsed
            time.sleep(0.5)  # Small delay to ensure media is ready
            self.media_list.add_media(media)
            self.list_player.set_media_list(self.media_list)
            self.list_player.set_playback_mode(
                vlc.PlaybackMode.loop
            )  # Ensure loop mode

            self.error_count = 0
            self.current_video = video_path
            self.save_last_played()
            logger.info(f"Video loaded successfully: {video_path}")

        except Exception as e:
            logger.error(f"Failed to load video: {e}")
            self.error_count += 1
            raise

    def play(self):
        """Play video with error recovery"""
        if not self.current_video:
            raise ValueError("No video loaded")

        try:
            self.list_player.play()
            self.is_playing = True
            logger.info("Video playback started")

        except Exception as e:
            logger.error(f"Playback error: {e}")
            if self.error_count < self.max_retry_attempts:
                logger.info("Attempting playback recovery...")
                self.error_count += 1
                time.sleep(self.retry_delay)
                try:
                    # Reload video and try again
                    self.load_video(self.current_video)
                    self.list_player.play()
                    self.is_playing = True
                    logger.info("Playback recovery successful")
                except Exception as retry_error:
                    logger.error(f"Recovery failed: {retry_error}")
                    raise
            else:
                raise RuntimeError("Max retry attempts reached")

    def pause(self):
        """Pause video with state verification"""
        if not self.current_video:
            raise ValueError("No video loaded")

        try:
            self.list_player.pause()
            # Verify pause state
            time.sleep(0.1)  # Brief delay to let state update
            if self.list_player.get_state() == vlc.State.Paused:
                self.is_playing = False
                logger.info("Video paused successfully")
            else:
                raise RuntimeError("Failed to verify pause state")

        except Exception as e:
            logger.error(f"Failed to pause video: {e}")
            raise

    def stop(self):
        """Stop video with cleanup"""
        if not self.current_video:
            raise ValueError("No video loaded")

        try:
            self.list_player.stop()
            self.is_playing = False
            self.error_count = 0  # Reset error count
            logger.info("Video stopped successfully")

        except Exception as e:
            logger.error(f"Failed to stop video: {e}")
            raise

    def get_status(self) -> Dict:
        """Get comprehensive player status"""
        if not self.current_video:
            return {
                "current_video": None,
                "status": PlayerState.NO_MEDIA,
                "is_playing": False,
                "is_looping": True,
                "error_count": self.error_count,
                "volume": 0,
            }

        try:
            player_state = self.list_player.get_state()
            volume = self.player.audio_get_volume()

            status = {
                "current_video": Path(self.current_video).name,
                "status": self._map_vlc_state(player_state),
                "is_playing": self.is_playing,
                "is_looping": True,
                "error_count": self.error_count,
                "volume": volume,
            }

            # Add position info if playing
            if self.is_playing:
                status["position"] = self.player.get_position()
                status["time"] = self.player.get_time()

            return status

        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"status": PlayerState.ERROR, "error": str(e)}

    def _map_vlc_state(self, state):
        """Map VLC states to PlayerState enum"""
        state_map = {
            vlc.State.Playing: PlayerState.PLAYING,
            vlc.State.Paused: PlayerState.PAUSED,
            vlc.State.Stopped: PlayerState.STOPPED,
            vlc.State.Error: PlayerState.ERROR,
        }
        return state_map.get(state, PlayerState.ERROR)

    def load_last_played(self):
        try:
            if self.last_played_file.exists():
                with open(self.last_played_file, "r") as f:
                    data = json.load(f)
                    if "last_video" in data:
                        video_path = self.upload_dir / data["last_video"]
                        if video_path.exists():
                            self.load_video(str(video_path))
                            self.play()  # Start playing the loaded video
                            logger.info(
                                f"Loaded and started playing last video: {data['last_video']}"
                            )
        except Exception as e:
            logger.error(f"Error loading last played video: {e}")

    def save_last_played(self):
        try:
            with open(self.last_played_file, "w") as f:
                json.dump({"last_video": Path(self.current_video).name}, f)
            logger.info(f"Saved last played video: {Path(self.current_video).name}")
        except Exception as e:
            logger.error(f"Error saving last played video: {e}")


# Create global video manager instance
video_manager = VideoManager()


class PlayRequest(BaseModel):
    video_name: str


app = FastAPI(title="Robust Video Looper API")

origins = [
    "http://localhost:3000",  # Replace with your frontend's address
    "http://127.0.0.1:3000",  # If using localhost with a different port
    "https://your-frontend-domain.com",  # Replace with production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies and credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(tv_controller.router, prefix="/tv", tags=["TV Schedule APIs"])
app.include_router(cec_routers, prefix="/tv", tags=["TV HDMI APIs"])


@app.post("/upload")
async def upload_video(file: UploadFile, background_tasks: BackgroundTasks):
    """Upload and validate video file"""
    if not file.filename:
        raise HTTPException(400, "No file provided")

    allowed_extensions = {".mp4", ".avi", ".mkv", ".mov"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            400, f"Unsupported file type. Allowed types: {allowed_extensions}"
        )

    file_path = video_manager.upload_dir / file.filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(500, f"Failed to save file: {str(e)}")

    try:
        video_manager.load_video(str(file_path))

        # Add cleanup task
        background_tasks.add_task(logger.info, f"Video uploaded: {file.filename}")

        return JSONResponse(
            {
                "message": "Video uploaded and loaded successfully",
                "filename": file.filename,
            }
        )
    except Exception as e:
        logger.error(f"Failed to load video: {e}")
        # Clean up failed upload
        file_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Failed to load video: {str(e)}")


@app.post("/play")
async def play_video(request: PlayRequest):
    """Play a video by name."""
    try:
        file_path = video_manager.upload_dir / request.video_name
        video_manager.load_video(str(file_path))
        video_manager.play()
        return {
            "status": "success",
            "message": f"Playing {request.video_name} in loop mode",
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/pause")
async def pause_video():
    """Pause video playback"""
    try:
        video_manager.pause()
        return {"message": "Video paused"}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Pause error: {e}")
        raise HTTPException(500, f"Failed to pause video: {str(e)}")


@app.post("/stop")
async def stop_video():
    """Stop video playback"""
    try:
        video_manager.stop()
        return {"message": "Video stopped"}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Stop error: {e}")
        raise HTTPException(500, f"Failed to stop video: {str(e)}")


@app.get("/status")
async def get_status():
    """Match the status format of main code."""
    status = video_manager.get_status()
    videos = list(video_manager.upload_dir.glob("*.mp4"))

    return {
        "current_video": status["current_video"],
        "is_playing": status["is_playing"],
        "is_paused": status["status"] == PlayerState.PAUSED,
        "is_looping": status["is_looping"],
        "available_videos": [f.name for f in videos],
        "date_uploaded": [
            datetime.fromtimestamp(f.stat().st_mtime).strftime("%I:%M %p %b %d %Y")
            for f in videos
        ],
    }


@app.post("/resume")
async def resume_video():
    try:
        status = video_manager.get_status()
        if status["status"] == PlayerState.PAUSED:
            video_manager.play()
            return {"status": "success", "message": "Video resumed"}
        raise HTTPException(status_code=400, detail="Video is not paused")
    except Exception as e:
        logger.error(f"Failed to resume video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/videos")
async def list_videos():
    """List all uploaded videos"""
    try:
        videos = [
            f.name
            for f in video_manager.upload_dir.glob("*")
            if f.suffix.lower() in {".mp4", ".avi", ".mkv", ".mov"}
        ]
        return {"videos": videos}
    except Exception as e:
        logger.error(f"Failed to list videos: {e}")
        raise HTTPException(500, f"Failed to list videos: {str(e)}")


@app.get("/preview")
async def get_preview():
    status = video_manager.get_status()
    if status["status"] != PlayerState.PLAYING or not status["current_video"]:
        raise HTTPException(status_code=404, detail="No video is currently playing")

    try:
        current_video = Path(status["current_video"])
        uploaded_video_dir = str(
            Path(video_manager.upload_dir).joinpath(current_video.name)
        )
        compressed_path = video_manager.compressed_dir / current_video.name

        if not compressed_path.exists():

            logger.info(f"Compressing video: {video_manager.current_video}")
            video_manager.compressor.compress_video(
                input_path=str(uploaded_video_dir),
                output_path=str(compressed_path),
            )
            logger.info(f"Compression complete: {video_manager.current_video}")

        return StreamingResponse(open(compressed_path, "rb"), media_type="video/mp4")
    except Exception as e:
        logger.error(f"Error streaming preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/video/{video_name}")
async def delete_video(video_name: str):
    try:
        video_path = video_manager.upload_dir / video_name
        compressed_path = video_manager.compressed_dir / video_name

        # Stop if currently playing
        if (
            video_manager.current_video
            and Path(video_manager.current_video).name == video_name
        ):
            video_manager.stop()
            video_manager.current_video = None

        # Delete files
        if video_path.exists():
            video_path.unlink()
        if compressed_path.exists():
            compressed_path.unlink()

        return {"status": "success", "message": f"Deleted {video_name}"}
    except Exception as e:
        logger.error(f"Failed to delete video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_ip_address() -> str:
    """Get the IP address of the first available network interface."""
    try:
        interfaces = [i for i in netifaces.interfaces() if i != "lo"]

        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                return addrs[netifaces.AF_INET][0]["addr"]

        return "127.0.0.1"
    except Exception as e:
        logger.error(f"Error getting IP address: {e}")
        return "127.0.0.1"


def register_service() -> Zeroconf:
    """Register the video server service using Zeroconf."""
    try:
        ip = get_ip_address()
        hostname = socket.gethostname()

        logger.info(f"Registering service with IP: {ip}")

        info = ServiceInfo(
            "_pivideo._tcp.local.",
            f"{hostname}._pivideo._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=5000,
            properties={"hostname": hostname},
        )

        zeroconf = Zeroconf()
        zeroconf.register_service(info)
        return zeroconf
    except Exception as e:
        logger.error(f"Error registering service: {e}")
        raise


if __name__ == "__main__":
    zeroconf = register_service()
    uvicorn.run(app, host="0.0.0.0", port=8000)
