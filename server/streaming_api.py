import json
import logging
import os
import socket
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import netifaces
import uvicorn
import vlc
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from zeroconf import ServiceInfo, Zeroconf

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

from utils.ffmpeg_compressor import VideoCompressor

from routers.control_tv import tv_controller


class VideoServer:
    def __init__(self, video_dir: str = "videos"):
        self.video_dir = Path(video_dir)
        self.compressed_dir = self.video_dir / "compressed"

        # Create necessary directories
        self.video_dir.mkdir(exist_ok=True)
        self.compressed_dir.mkdir(exist_ok=True)

        # Initialize VLC instance once, don't create new instance on each play
        self.vlc_instance = vlc.Instance(
            "--input-repeat=-1"
        )  # Set very high repeat count
        self.player = self.vlc_instance.media_player_new()

        # Server state
        self.current_video: Optional[str] = None
        self.current_video_path: Optional[Path] = None
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.last_played_file = Path("last_played.json")
        self.last_position: int = 0
        self.loop_enabled: bool = True  # Default to loop enabled

        # Initialize video compressor
        self.compressor = VideoCompressor(target_resolution=240, target_fps=10)

        # Load last played video if exists
        self.load_last_played()

        logger.info("VideoServer initialized successfully with looping enabled")

    # class VideoServer:
    #     def __init__(self, video_dir: str = "videos"):
    #         self.video_dir = Path(video_dir)
    #         self.compressed_dir = self.video_dir / "compressed"

    #         # Create necessary directories
    #         self.video_dir.mkdir(exist_ok=True)
    #         self.compressed_dir.mkdir(exist_ok=True)

    #         # Initialize VLC instance with loop option
    #         self.vlc_instance = vlc.Instance(
    #             "--input-repeat=-1"
    #         )  # Set very high repeat count
    #         self.player = self.vlc_instance.media_player_new()

    #         # Server state
    #         self.current_video: Optional[str] = None
    #         self.current_video_path: Optional[Path] = None
    #         self.is_playing: bool = False
    #         self.is_paused: bool = False
    #         self.last_played_file = Path("last_played.json")
    #         self.last_position: int = 0
    #         self.loop_enabled: bool = True  # Default to loop enabled

    #         # Initialize video compressor
    #         self.compressor = VideoCompressor(target_resolution=240, target_fps=10)

    #         # Load last played video if exists
    #         self.load_last_played()

    #         logger.info("VideoServer initialized successfully with looping enabled")

    def get_compressed_path(self, video_name: str) -> Path:
        """Get the path for the compressed version of a video."""
        return self.compressed_dir / video_name.replace(".mp4", "_compressed.mp4")

    def load_last_played(self):
        """Load and automatically play the last played video on startup."""
        try:
            if self.last_played_file.exists():
                with open(self.last_played_file, "r") as f:
                    data = json.load(f)
                    if "last_video" in data:
                        self.play_video(data["last_video"])
                        logger.info(f"Loaded last played video: {data['last_video']}")
        except Exception as e:
            logger.error(f"Error loading last played video: {e}")

    def save_last_played(self):
        """Save the currently playing video to persist between restarts."""
        try:
            with open(self.last_played_file, "w") as f:
                json.dump({"last_video": self.current_video}, f)
            logger.info(f"Saved last played video: {self.current_video}")
        except Exception as e:
            logger.error(f"Error saving last played video: {e}")

    def play_video(self, video_name: str) -> bool:
        """Play a video from the video directory with looping enabled."""
        video_path = self.video_dir / video_name
        if not video_path.exists():
            logger.error(f"Video not found: {video_name}")
            return False

        try:
            # If there's a video currently playing or paused, stop it first
            if self.current_video:
                self.stop_video()

            # Create a new media instance with the video
            media = self.vlc_instance.media_new(str(video_path))

            # Set media options for looping
            media.add_option("input-repeat=-1")  # Set very high repeat count

            # Set the media to the player
            self.player.set_media(media)

            # Start playback
            self.player.play()

            self.current_video = video_name
            self.current_video_path = video_path
            self.is_playing = True
            self.is_paused = False
            self.last_position = 0
            self.save_last_played()

            logger.info(f"Started playing video in loop mode: {video_name}")
            return True

        except Exception as e:
            logger.error(f"Error playing video {video_name}: {e}")
            return False

    def pause_video(self) -> bool:
        """Pause the currently playing video."""
        try:
            if self.is_playing and not self.is_paused:
                self.player.pause()
                self.is_paused = True
                self.last_position = self.player.get_time()
                logger.info(
                    f"Paused video: {self.current_video} at position {self.last_position}ms"
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Error pausing video: {e}")
            return False

    def resume_video(self) -> bool:
        """Resume the paused video."""
        try:
            if self.is_paused:
                self.player.play()
                self.is_paused = False
                logger.info(f"Resumed video: {self.current_video}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resuming video: {e}")
            return False

    def stop_video(self):
        """Stop the currently playing video."""
        try:
            self.player.stop()
            self.is_playing = False
            self.is_paused = False
            self.last_position = 0
            logger.info(f"Stopped video: {self.current_video}")
        except Exception as e:
            logger.error(f"Error stopping video: {e}")

    def set_loop(self, enabled: bool) -> bool:
        """Enable or disable video looping."""
        try:
            self.loop_enabled = enabled
            if self.current_video:
                # Restart the current video with new loop setting
                current = self.current_video
                self.stop_video()
                self.play_video(current)
            logger.info(f"Video looping {'enabled' if enabled else 'disabled'}")
            return True
        except Exception as e:
            logger.error(f"Error setting loop mode: {e}")
            return False

    def get_status(self) -> Dict:
        """Get the current player status."""
        try:
            videos = list(self.video_dir.glob("*.mp4"))
            current_position = (
                self.player.get_time() if self.is_playing or self.is_paused else 0
            )
            return {
                "current_video": self.current_video,
                "is_playing": self.is_playing,
                "is_paused": self.is_paused,
                "is_looping": self.loop_enabled,
                "current_position": current_position,
                "available_videos": [f.name for f in videos],
                "date_uploaded": [
                    datetime.fromtimestamp(f.stat().st_mtime).strftime(
                        "%I:%M %p %b %d %Y"
                    )
                    for f in videos
                ],
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {}

    def __del__(self):
        """Cleanup on shutdown."""
        logger.info("Shutting down VideoServer")
        self.stop_video()


# FastAPI application setup
app = FastAPI(title="Video Server API", version="1.0.0")
app.include_router(tv_controller.router, prefix="/tv", tags=["TV Schedule APIs"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

video_server = VideoServer()


class PlayRequest(BaseModel):
    video_name: str


class LoopRequest(BaseModel):
    enabled: bool


@app.post("/play")
async def play_video(request: PlayRequest):
    """Play a video by name."""
    success = video_server.play_video(request.video_name)
    if not success:
        raise HTTPException(status_code=404, detail="Video not found")
    return {
        "status": "success",
        "message": f"Playing {request.video_name} in loop mode",
    }


@app.post("/pause")
async def pause_video():
    """Pause the currently playing video."""
    if not video_server.current_video:
        raise HTTPException(status_code=404, detail="No video is currently playing")
    success = video_server.pause_video()
    if success:
        return {"status": "success", "message": "Video paused"}
    raise HTTPException(
        status_code=400, detail="Video is not playing or already paused"
    )


@app.post("/resume")
async def resume_video():
    """Resume the paused video."""
    if not video_server.current_video:
        raise HTTPException(status_code=404, detail="No video is currently loaded")
    success = video_server.resume_video()
    if success:
        return {"status": "success", "message": "Video resumed"}
    raise HTTPException(status_code=400, detail="Video is not paused")


@app.post("/loop")
async def set_loop(request: LoopRequest):
    """Enable or disable video looping."""
    success = video_server.set_loop(request.enabled)
    if success:
        return {
            "status": "success",
            "message": f"Video looping {'enabled' if request.enabled else 'disabled'}",
        }
    raise HTTPException(status_code=500, detail="Failed to set loop mode")


@app.post("/stop")
async def stop_video():
    """Stop the currently playing video."""
    video_server.stop_video()
    return {"status": "success", "message": "Video stopped"}


@app.get("/status")
async def get_status():
    """Get the current server status."""
    return video_server.get_status()


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload a new video file."""
    try:
        file_path = video_server.video_dir / file.filename
        contents = await file.read()

        with open(file_path, "wb") as f:
            f.write(contents)

        logger.info(f"Successfully uploaded video: {file.filename}")
        return {"status": "success", "message": f"Uploaded {file.filename}"}
    except Exception as e:
        logger.error(f"Error uploading video {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/video/{video_name}")
async def delete_video(video_name: str):
    """Delete a video and its compressed version."""
    success = video_server.delete_video(video_name)
    if not success:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"status": "success", "message": f"Deleted {video_name}"}


@app.get("/preview")
async def get_preview():
    """Stream the compressed version of the currently playing video."""
    if not video_server.is_playing or not video_server.current_video_path:
        raise HTTPException(status_code=404, detail="No video is currently playing")

    try:
        compressed_path = video_server.get_compressed_path(video_server.current_video)

        # Create compressed version if it doesn't exist
        if not compressed_path.exists():
            logger.info(f"Compressing video: {video_server.current_video}")
            video_server.compressor.compress_video(
                input_path=str(video_server.current_video_path),
                output_path=str(compressed_path),
            )
            logger.info(f"Compression complete: {video_server.current_video}")

        return StreamingResponse(
            open(compressed_path, "rb"),
            media_type="video/mp4",
        )
    except Exception as e:
        logger.error(f"Error streaming preview: {e}")
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
    uvicorn.run("streaming_api:app", host="0.0.0.0", port=8000, reload=False)
